from datetime import datetime, timezone

from bson import ObjectId
from fastapi import APIRouter, HTTPException, Depends

from app.core.database import reports_col, templates_col
from app.core.security import get_current_user, require_role
from app.schemas.radflow import ReportOut, ReportUpdate, RiskUpdate

router = APIRouter(prefix="/reports", tags=["Reports"])

# ── Role constants ─────────────────────────────────────────────────────────────
# Matches the product spec exactly:
#
#   hybrid      → full access (primary hackathon role)
#   radiologist → view, edit, generate, finalise, apply templates, assign risk
#   sonographer → view + edit findings only
#                 CANNOT finalise, assign risk, or apply templates

_CAN_READ   = ("hybrid", "radiologist", "sonographer")
_CAN_EDIT   = ("hybrid", "radiologist", "sonographer")
_CAN_REPORT = ("hybrid", "radiologist")   # apply template
_CAN_FINAL  = ("hybrid", "radiologist")   # finalise
_CAN_RISK   = ("hybrid", "radiologist")   # assign risk level


def _serialize(doc: dict) -> ReportOut:
    return ReportOut(
        id=str(doc["_id"]),
        scan_id=doc["scan_id"],
        patient_id=doc["patient_id"],
        patient_name=doc.get("patient_name", ""),
        scan_type=doc["scan_type"],
        clinical_indication=doc["clinical_indication"],
        findings=doc.get("findings", ""),
        impression=doc.get("impression", ""),
        risk_level=doc.get("risk_level"),
        template_id=doc.get("template_id"),
        is_final=doc.get("is_final", False),
        created_by=doc["created_by"],
        created_at=doc["created_at"],
        finalised_at=doc.get("finalised_at"),
    )


async def _get_report_or_404(report_id: str) -> dict:
    try:
        oid = ObjectId(report_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid report ID")
    doc = await reports_col().find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=404, detail="Report not found")
    return doc


# ── GET /reports/:id ───────────────────────────────────────────────────────────
# All roles can read reports

@router.get("/{report_id}", response_model=ReportOut)
async def get_report(
    report_id: str,
    current_user: dict = Depends(require_role(*_CAN_READ)),
):
    return _serialize(await _get_report_or_404(report_id))


# ── GET /reports/by-scan/:scan_id ──────────────────────────────────────────────

@router.get("/by-scan/{scan_id}", response_model=ReportOut)
async def get_report_by_scan(
    scan_id: str,
    current_user: dict = Depends(require_role(*_CAN_READ)),
):
    doc = await reports_col().find_one({"scan_id": scan_id})
    if not doc:
        raise HTTPException(status_code=404, detail="No report found for this scan")
    return _serialize(doc)


# ── PATCH /reports/:id ─────────────────────────────────────────────────────────
# All roles can edit findings and impression (sonographer can edit, cannot finalise)

@router.patch("/{report_id}", response_model=ReportOut)
async def update_report(
    report_id: str,
    body: ReportUpdate,
    current_user: dict = Depends(require_role(*_CAN_EDIT)),
):
    doc = await _get_report_or_404(report_id)

    if doc.get("is_final"):
        raise HTTPException(status_code=400, detail="Cannot edit a finalised report")

    updates: dict = {"updated_at": datetime.now(timezone.utc)}
    if body.findings is not None:
        updates["findings"] = body.findings
    if body.impression is not None:
        updates["impression"] = body.impression

    await reports_col().update_one({"_id": doc["_id"]}, {"$set": updates})
    updated = await reports_col().find_one({"_id": doc["_id"]})
    return _serialize(updated)


# ── PATCH /reports/:id/risk ────────────────────────────────────────────────────
# SONOGRAPHER BLOCKED — only hybrid and radiologist can assign risk

@router.patch("/{report_id}/risk", response_model=ReportOut)
async def set_risk_level(
    report_id: str,
    body: RiskUpdate,
    current_user: dict = Depends(require_role(*_CAN_RISK)),
):
    doc = await _get_report_or_404(report_id)
    await reports_col().update_one(
        {"_id": doc["_id"]},
        {"$set": {"risk_level": body.risk_level, "updated_at": datetime.now(timezone.utc)}},
    )
    updated = await reports_col().find_one({"_id": doc["_id"]})
    return _serialize(updated)


# ── POST /reports/:id/apply-template ──────────────────────────────────────────
# SONOGRAPHER BLOCKED — only hybrid and radiologist

@router.post("/{report_id}/apply-template/{template_id}", response_model=ReportOut)
async def apply_template(
    report_id: str,
    template_id: str,
    current_user: dict = Depends(require_role(*_CAN_REPORT)),
):
    doc = await _get_report_or_404(report_id)

    try:
        tmpl = await templates_col().find_one({"_id": ObjectId(template_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid template ID")

    if not tmpl:
        raise HTTPException(status_code=404, detail="Template not found")

    template_structure = tmpl.get("structure", [])
    original_findings = doc.get("findings", "")

    if template_structure:
        reformatted = "\n\n".join(
            f"[{section}]\n" for section in template_structure
        ) + "\n\n" + original_findings
    else:
        reformatted = original_findings

    await reports_col().update_one(
        {"_id": doc["_id"]},
        {"$set": {
            "template_id": template_id,
            "findings": reformatted,
            "updated_at": datetime.now(timezone.utc),
        }},
    )
    updated = await reports_col().find_one({"_id": doc["_id"]})
    return _serialize(updated)


# ── POST /reports/:id/finalize ─────────────────────────────────────────────────
# SONOGRAPHER BLOCKED — only hybrid and radiologist can finalise

@router.post("/{report_id}/finalize", response_model=ReportOut)
async def finalize_report(
    report_id: str,
    current_user: dict = Depends(require_role(*_CAN_FINAL)),
):
    doc = await _get_report_or_404(report_id)

    if doc.get("is_final"):
        raise HTTPException(status_code=400, detail="Report is already finalised")

    if not doc.get("impression", "").strip():
        raise HTTPException(
            status_code=422,
            detail="Impression is required before finalising",
        )

    now = datetime.now(timezone.utc)
    await reports_col().update_one(
        {"_id": doc["_id"]},
        {"$set": {"is_final": True, "finalised_at": now, "updated_at": now}},
    )
    updated = await reports_col().find_one({"_id": doc["_id"]})
    return _serialize(updated)
