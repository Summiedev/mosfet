from datetime import datetime, timedelta, timezone
from typing import Optional

from bson import ObjectId
from fastapi import APIRouter, HTTPException, Depends, Query

from app.core.database import scans_col, patients_col, reports_col
from app.core.security import get_current_user
from app.schemas.radflow import (
    ScanCreate, ScanUpdate, ScanOut, ValidationResult,
    DashboardResponse, AIEventsResponse,
)
from app.services.checklist_service import get_checklist, get_required_keys
from app.services.ai_service import get_ai_events_for_scan
from app.services.report_service import generate_report_document

router = APIRouter(tags=["Scans"])


# ── Helpers ───────────────────────────────────────────────────────────────────

async def _get_scan_or_404(scan_id: str) -> dict:
    try:
        oid = ObjectId(scan_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid scan ID")
    doc = await scans_col().find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=404, detail="Scan session not found")
    return doc


async def _serialize_scan(doc: dict) -> ScanOut:
    patient = await patients_col().find_one({"_id": doc["patient_id"]})
    return ScanOut(
        id=str(doc["_id"]),
        patient_id=str(doc["patient_id"]),
        patient_name=patient["name"] if patient else "Unknown",
        scan_type=doc["scan_type"],
        clinical_indication=doc["clinical_indication"],
        status=doc["status"],
        checklist=doc.get("checklist", []),
        transcript=doc.get("transcript", ""),
        captured_frames=doc.get("captured_frames", []),
        ai_flags=doc.get("ai_flags", []),
        created_by=str(doc["created_by"]),
        created_at=doc["created_at"],
        completed_at=doc.get("completed_at"),
    )


# ── POST /scans ───────────────────────────────────────────────────────────────

@router.post("/scans", response_model=ScanOut, status_code=201)
async def create_scan(
    body: ScanCreate,
    current_user: dict = Depends(get_current_user),
):
    # Verify patient exists
    try:
        patient_oid = ObjectId(body.patient_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid patient ID")

    patient = await patients_col().find_one({"_id": patient_oid})
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    now = datetime.now(timezone.utc)
    doc = {
        "patient_id": patient_oid,
        "scan_type": body.scan_type,
        "clinical_indication": body.clinical_indication,
        "status": "pending",
        "checklist": get_checklist(body.scan_type),
        "transcript": "",
        "captured_frames": [],
        "ai_flags": [],
        "created_by": ObjectId(current_user["id"]),
        "created_at": now,
        "updated_at": now,
        "completed_at": None,
    }

    result = await scans_col().insert_one(doc)
    doc["_id"] = result.inserted_id
    return await _serialize_scan(doc)


# ── GET /scans/:id ───────────────────────────────────────────────────────────

@router.get("/scans/{scan_id}", response_model=ScanOut)
async def get_scan(
    scan_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    Fetch a single scan session by ID.
    Used by the scan view on load to hydrate the header
    (patient name, scan type, clinical indication, status).
    """
    doc = await _get_scan_or_404(scan_id)
    return await _serialize_scan(doc)


# ── PATCH /scans/:id ──────────────────────────────────────────────────────────

@router.patch("/scans/{scan_id}", response_model=ScanOut)
async def update_scan(
    scan_id: str,
    body: ScanUpdate,
    current_user: dict = Depends(get_current_user),
):
    doc = await _get_scan_or_404(scan_id)

    if doc["status"] == "completed":
        raise HTTPException(status_code=400, detail="Cannot update a completed scan")

    updates: dict = {"status": "in_progress", "updated_at": datetime.now(timezone.utc)}

    if body.checklist is not None:
        updates["checklist"] = [item.model_dump() for item in body.checklist]
    if body.transcript is not None:
        updates["transcript"] = body.transcript
    if body.captured_frames is not None:
        updates["captured_frames"] = [f.model_dump() for f in body.captured_frames]
    if body.ai_flags is not None:
        updates["ai_flags"] = [e.model_dump() for e in body.ai_flags]

    await scans_col().update_one({"_id": doc["_id"]}, {"$set": updates})
    updated = await scans_col().find_one({"_id": doc["_id"]})
    return await _serialize_scan(updated)


# ── POST /scans/:id/validate ──────────────────────────────────────────────────

@router.post("/scans/{scan_id}/validate", response_model=ValidationResult)
async def validate_scan(
    scan_id: str,
    current_user: dict = Depends(get_current_user),
):
    doc = await _get_scan_or_404(scan_id)
    checklist = doc.get("checklist", [])
    scan_type = doc.get("scan_type", "")
    required_keys = get_required_keys(scan_type)

    # Build lookup of completed items
    completed_map = {
        item["key"]: item.get("completed", False)
        for item in checklist
    }

    missing = [key for key in required_keys if not completed_map.get(key)]

    warnings = []
    if not doc.get("transcript", "").strip():
        warnings.append("No voice transcript recorded — consider adding findings manually")
    if not doc.get("captured_frames"):
        warnings.append("No frames captured — images are recommended for reporting")

    return ValidationResult(
        valid=len(missing) == 0,
        missing_fields=missing,
        warnings=warnings,
    )


# ── POST /scans/:id/complete ──────────────────────────────────────────────────

@router.post("/scans/{scan_id}/complete", response_model=ScanOut)
async def complete_scan(
    scan_id: str,
    override: bool = Query(False, description="Override validation and complete anyway"),
    current_user: dict = Depends(get_current_user),
):
    doc = await _get_scan_or_404(scan_id)

    if doc["status"] == "completed":
        raise HTTPException(status_code=400, detail="Scan already completed")

    # Run validation unless overridden
    if not override:
        checklist = doc.get("checklist", [])
        required_keys = get_required_keys(doc.get("scan_type", ""))
        completed_map = {item["key"]: item.get("completed", False) for item in checklist}
        missing = [k for k in required_keys if not completed_map.get(k)]

        if missing:
            raise HTTPException(
                status_code=422,
                detail={
                    "message": "Scan has incomplete required fields. Pass ?override=true to complete anyway.",
                    "missing_fields": missing,
                },
            )

    now = datetime.now(timezone.utc)
    await scans_col().update_one(
        {"_id": doc["_id"]},
        {"$set": {"status": "completed", "completed_at": now, "updated_at": now}},
    )

    # Auto-generate report
    patient = await patients_col().find_one({"_id": doc["patient_id"]})
    report_doc = generate_report_document(doc, patient or {}, current_user["full_name"])
    await reports_col().insert_one(report_doc)

    updated = await scans_col().find_one({"_id": doc["_id"]})
    return await _serialize_scan(updated)


# ── GET /scans/:id/ai-events ──────────────────────────────────────────────────

@router.get("/scans/{scan_id}/ai-events", response_model=AIEventsResponse)
async def get_ai_events(
    scan_id: str,
    elapsed: Optional[float] = Query(
        None,
        description="Seconds elapsed since scan start. Returns only events up to this time."
    ),
    current_user: dict = Depends(get_current_user),
):
    doc = await _get_scan_or_404(scan_id)
    events = get_ai_events_for_scan(doc["scan_type"], elapsed_seconds=elapsed)
    return AIEventsResponse(scan_id=scan_id, events=events)


# ── GET /dashboard ────────────────────────────────────────────────────────────

# Risk priority order — used to sort scans so critical cases float to the top
_RISK_ORDER = {"critical": 0, "high": 1, "moderate": 2, "low": 3, None: 4}


async def _get_report_risk(scan_id: str) -> str | None:
    """Fetch the risk_level from the report linked to this scan, if any."""
    doc = await reports_col().find_one({"scan_id": str(scan_id)}, {"risk_level": 1})
    return doc.get("risk_level") if doc else None


@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard(current_user: dict = Depends(get_current_user)):
    user_oid = ObjectId(current_user["id"])
    now = datetime.now(timezone.utc)
    cutoff_48h = now - timedelta(hours=48)

    # ── Pending scans (any age) ───────────────────────────────────────────────
    pending_docs = await scans_col().find({
        "created_by": user_oid,
        "status": {"$in": ["pending", "in_progress"]},
    }).sort("created_at", -1).to_list(length=50)

    # ── Recently completed (within 48 h) ──────────────────────────────────────
    recent_docs = await scans_col().find({
        "created_by": user_oid,
        "status": "completed",
        "completed_at": {"$gte": cutoff_48h},
    }).sort("completed_at", -1).to_list(length=20)

    # ── Count today's scans ───────────────────────────────────────────────────
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    total_today = await scans_col().count_documents({
        "created_by": user_oid,
        "created_at": {"$gte": today_start},
    })

    # ── Attach risk level from linked report to each scan doc ─────────────────
    # We add a temporary _risk field for sorting — not exposed in the schema.
    for doc in pending_docs + recent_docs:
        doc["_risk"] = await _get_report_risk(str(doc["_id"]))

    # ── Critical cases — scans with high or critical risk reports ─────────────
    critical_docs = [
        d for d in recent_docs
        if d.get("_risk") in ("high", "critical")
    ]

    # ── Sort: critical/high risk float to top within each list ────────────────
    pending_docs.sort(key=lambda d: _RISK_ORDER.get(d.get("_risk"), 4))
    recent_docs.sort(key=lambda d: _RISK_ORDER.get(d.get("_risk"), 4))

    pending_scans    = [await _serialize_scan(d) for d in pending_docs]
    recent_completed = [await _serialize_scan(d) for d in recent_docs]
    critical_cases   = [await _serialize_scan(d) for d in critical_docs]

    return DashboardResponse(
        pending_scans=pending_scans,
        recent_completed=recent_completed,
        critical_cases=critical_cases,
        total_today=total_today,
    )
