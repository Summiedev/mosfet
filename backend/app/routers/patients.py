from datetime import datetime, timezone

from bson import ObjectId
from fastapi import APIRouter, HTTPException, Depends

from app.core.database import patients_col
from app.core.security import get_current_user
from app.schemas.radflow import PatientCreate, PatientOut

router = APIRouter(prefix="/patients", tags=["Patients"])


def _serialize(doc: dict) -> PatientOut:
    return PatientOut(
        id=str(doc["_id"]),
        name=doc["name"],
        age=doc.get("age"),
        sex=doc.get("sex"),
        phone=doc.get("phone"),
        created_by=str(doc["created_by"]),
        created_at=doc["created_at"],
    )


# ── POST /patients ────────────────────────────────────────────────────────────

@router.post("", response_model=PatientOut, status_code=201)
async def create_patient(
    body: PatientCreate,
    current_user: dict = Depends(get_current_user),
):
    now = datetime.now(timezone.utc)
    doc = {
        **body.model_dump(),
        "created_by": ObjectId(current_user["id"]),
        "created_at": now,
        "updated_at": now,
    }
    result = await patients_col().insert_one(doc)
    doc["_id"] = result.inserted_id
    return _serialize(doc)


# ── GET /patients/:id ─────────────────────────────────────────────────────────

@router.get("/{patient_id}", response_model=PatientOut)
async def get_patient(
    patient_id: str,
    current_user: dict = Depends(get_current_user),
):
    try:
        oid = ObjectId(patient_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid patient ID")

    doc = await patients_col().find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=404, detail="Patient not found")

    return _serialize(doc)
