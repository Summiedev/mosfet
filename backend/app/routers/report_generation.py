"""
Report generation router.

POST /reports/generate/:scanId  — assemble full structured report from scan data.
                                  SONOGRAPHER BLOCKED — only hybrid + radiologist.
"""
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException

from app.core.database import scans_col, patients_col, reports_col, media_col
from app.core.security import require_role
from app.schemas.radflow import ReportGenerateResponse
from app.services.report_service import generate_report_document

router = APIRouter(prefix="/reports", tags=["Report Generation"])

_CAN_GENERATE = ("hybrid", "radiologist")


@router.post("/generate/{scan_id}", response_model=ReportGenerateResponse, status_code=201)
async def generate_report(
    scan_id: str,
    current_user: dict = Depends(require_role(*_CAN_GENERATE)),
):
    """
    Assembles a structured report from scan data.
    SONOGRAPHER BLOCKED — returns 403 if role is sonographer.

    If a report already exists for this scan, returns it (idempotent).
    """
    try:
        scan_oid = ObjectId(scan_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid scan ID")

    scan = await scans_col().find_one({"_id": scan_oid})
    if not scan:
        raise HTTPException(status_code=404, detail="Scan session not found")

    if scan["status"] not in ("completed", "in_progress"):
        raise HTTPException(
            status_code=422,
            detail="Report can only be generated for scans that are in_progress or completed",
        )

    # Return existing report if already generated (idempotent)
    existing = await reports_col().find_one({"scan_id": scan_id})
    if existing:
        return _serialize(existing)

    patient = await patients_col().find_one({"_id": scan["patient_id"]})
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Pull media URLs from media collection
    media_docs = await media_col().find({"scan_id": scan_id}).to_list(length=50)
    media_urls = [m["url"] for m in media_docs]

    doc = generate_report_document(
        scan=scan,
        patient=patient,
        radiologist_name=current_user["full_name"],
        media_urls=media_urls,
    )

    result = await reports_col().insert_one(doc)
    doc["_id"] = result.inserted_id
    return _serialize(doc)


def _serialize(doc: dict) -> ReportGenerateResponse:
    return ReportGenerateResponse(
        id=str(doc["_id"]),
        scan_id=doc["scan_id"],
        patient_id=doc["patient_id"],
        patient_name=doc.get("patient_name", ""),
        scan_type=doc["scan_type"],
        clinical_indication=doc["clinical_indication"],
        technique=doc.get("technique", ""),
        findings=doc.get("findings", ""),
        impression=doc.get("impression", ""),
        risk_level=doc.get("risk_level"),
        template_id=doc.get("template_id"),
        captured_frame_urls=doc.get("captured_frame_urls", []),
        is_final=doc.get("is_final", False),
        created_by=str(doc["created_by"]),
        created_at=doc["created_at"],
        finalised_at=doc.get("finalised_at"),
    )
