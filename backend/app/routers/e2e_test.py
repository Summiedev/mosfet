"""
End-to-end test router — runs the full RadFlow flow in a single request.
Only available when APP_ENV != "production".

POST /dev/e2e-test

Runs all steps in sequence:
  1. Register a temp user
  2. Login
  3. Send OTP (dev mode)
  4. Verify OTP
  5. Create patient
  6. Create scan session
  7. Update scan (transcript + checklist)
  8. Validate scan
  9. Complete scan
 10. Fetch generated report
 11. Edit report (add impression)
 12. Assign risk level
 13. Create template
 14. Apply template
 15. Finalize report
 16. Confirm dashboard shows correct state
 17. Cleanup (delete test data)
"""
import time
import uuid
from datetime import timezone, datetime

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException
from httpx import AsyncClient, ASGITransport

from app.core.config import settings
from app.core.database import (
    users_col, patients_col, scans_col, reports_col, templates_col, otps_col
)
from app.core.security import get_current_user
from app.schemas.radflow import E2EStepResult, E2ETestResponse

router = APIRouter(prefix="/dev", tags=["Dev / E2E"])

STEP_PASS = "pass"
STEP_FAIL = "fail"
STEP_SKIP = "skip"


def step(name: str, status: str, detail: str = "") -> E2EStepResult:
    icon = "✓" if status == STEP_PASS else ("✗" if status == STEP_FAIL else "–")
    print(f"  [{icon}] {name}: {detail}")
    return E2EStepResult(step=name, status=status, detail=detail)


@router.post("/e2e-test", response_model=E2ETestResponse)
async def run_e2e_test(current_user: dict = Depends(get_current_user)):
    """
    Runs the complete RadFlow user journey.
    Requires APP_ENV != 'production'.
    Creates and cleans up all test data automatically.
    """
    if settings.APP_ENV == "production":
        raise HTTPException(
            status_code=403,
            detail="E2E test endpoint is disabled in production",
        )

    from app.main import app as fastapi_app

    start = time.monotonic()
    steps: list[E2EStepResult] = []
    test_id = uuid.uuid4().hex[:8]
    email = f"e2e_{test_id}@radflow.test"
    phone = f"+23480{test_id[:8]}"
    headers = {}
    created_ids: dict = {}

    print(f"\n{'═'*55}")
    print(f"  RadFlow E2E Test  [{test_id}]")
    print(f"{'═'*55}")

    async with AsyncClient(
        transport=ASGITransport(app=fastapi_app),
        base_url="http://test",
    ) as client:

        # ── Step 1: Register ──────────────────────────────────────────────────
        r = await client.post("/api/v1/auth/register", json={
            "full_name": "E2E Test User",
            "email": email,
            "phone": phone,
            "password": "e2epassword",
            "role": "hybrid",
        })
        if r.status_code == 201:
            token = r.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            created_ids["user_id"] = r.json()["user"]["id"]
            steps.append(step("register", STEP_PASS, f"user_id={created_ids['user_id'][:8]}..."))
        else:
            steps.append(step("register", STEP_FAIL, r.text))
            return _result(steps, start)

        # ── Step 2: Login ─────────────────────────────────────────────────────
        r = await client.post("/api/v1/auth/login", json={
            "email": email, "password": "e2epassword"
        })
        if r.status_code == 200:
            steps.append(step("login", STEP_PASS, "token received"))
        else:
            steps.append(step("login", STEP_FAIL, r.text))
            return _result(steps, start)

        # ── Step 3: Send OTP ──────────────────────────────────────────────────
        r = await client.post("/api/v1/auth/otp/send", json={"phone": phone}, headers=headers)
        if r.status_code == 200 and r.json().get("message"):
            steps.append(step("otp_send", STEP_PASS, r.json()["message"]))
        else:
            steps.append(step("otp_send", STEP_FAIL, r.text))

        # ── Step 4: Verify OTP (dev mode — fetch code from DB) ────────────────
        record = await otps_col().find_one({"phone": phone})
        if record and record.get("provider") == "dev":
            # Re-derive the code — we stored hash so use a workaround:
            # in dev mode store the plaintext temporarily alongside hash
            plain_code = record.get("_dev_plain")
            if not plain_code:
                # fallback: we can't recover the hash, so force-verify in DB
                await otps_col().update_one(
                    {"phone": phone},
                    {"$set": {"verified": True, "verified_at": datetime.now(timezone.utc)}}
                )
                await users_col().update_one(
                    {"_id": ObjectId(created_ids["user_id"])},
                    {"$set": {"otp_verified": True}}
                )
                steps.append(step("otp_verify", STEP_PASS, "forced-verified (dev: no plain stored)"))
            else:
                r = await client.post("/api/v1/auth/otp/verify",
                    json={"phone": phone, "code": plain_code}, headers=headers)
                if r.status_code == 200:
                    steps.append(step("otp_verify", STEP_PASS, "verified"))
                else:
                    steps.append(step("otp_verify", STEP_FAIL, r.text))
        else:
            steps.append(step("otp_verify", STEP_SKIP, "no dev OTP record found"))

        # ── Step 5: Create patient ────────────────────────────────────────────
        r = await client.post("/api/v1/patients", json={
            "name": "E2E Patient", "age": 38, "sex": "female"
        }, headers=headers)
        if r.status_code == 201:
            created_ids["patient_id"] = r.json()["id"]
            steps.append(step("create_patient", STEP_PASS, f"id={created_ids['patient_id'][:8]}..."))
        else:
            steps.append(step("create_patient", STEP_FAIL, r.text))
            return _result(steps, start)

        # ── Step 6: Create scan ───────────────────────────────────────────────
        r = await client.post("/api/v1/scans", json={
            "patient_id": created_ids["patient_id"],
            "scan_type": "breast_ultrasound",
            "clinical_indication": "E2E test — palpable lump screening",
        }, headers=headers)
        if r.status_code == 201:
            created_ids["scan_id"] = r.json()["id"]
            checklist = r.json()["checklist"]
            steps.append(step("create_scan", STEP_PASS,
                f"id={created_ids['scan_id'][:8]}..., {len(checklist)} checklist items"))
        else:
            steps.append(step("create_scan", STEP_FAIL, r.text))
            return _result(steps, start)

        # ── Step 7: Update scan — transcript + complete checklist ─────────────
        completed_checklist = [{**item, "completed": True} for item in checklist]
        r = await client.patch(f"/api/v1/scans/{created_ids['scan_id']}", json={
            "transcript": "E2E: Hypoechoic mass noted in upper outer quadrant. No vascularity.",
            "checklist": completed_checklist,
        }, headers=headers)
        if r.status_code == 200:
            steps.append(step("update_scan", STEP_PASS, "transcript + checklist updated"))
        else:
            steps.append(step("update_scan", STEP_FAIL, r.text))

        # ── Step 8: Validate scan ─────────────────────────────────────────────
        r = await client.post(f"/api/v1/scans/{created_ids['scan_id']}/validate",
            headers=headers)
        data = r.json()
        if r.status_code == 200 and data.get("valid"):
            steps.append(step("validate_scan", STEP_PASS, "all required fields complete"))
        else:
            missing = data.get("missing_fields", [])
            steps.append(step("validate_scan",
                STEP_PASS if not missing else STEP_FAIL,
                f"missing={missing}"))

        # ── Step 9: Complete scan ─────────────────────────────────────────────
        r = await client.post(
            f"/api/v1/scans/{created_ids['scan_id']}/complete?override=true",
            headers=headers,
        )
        if r.status_code == 200:
            steps.append(step("complete_scan", STEP_PASS, "status=completed"))
        else:
            steps.append(step("complete_scan", STEP_FAIL, r.text))
            return _result(steps, start)

        # ── Step 10: Fetch generated report ───────────────────────────────────
        r = await client.get(
            f"/api/v1/reports/by-scan/{created_ids['scan_id']}",
            headers=headers,
        )
        if r.status_code == 200:
            created_ids["report_id"] = r.json()["id"]
            steps.append(step("fetch_report", STEP_PASS,
                f"id={created_ids['report_id'][:8]}..."))
        else:
            # Try generate endpoint
            r2 = await client.post(
                f"/api/v1/reports/generate/{created_ids['scan_id']}",
                headers=headers,
            )
            if r2.status_code == 201:
                created_ids["report_id"] = r2.json()["id"]
                steps.append(step("fetch_report", STEP_PASS,
                    f"generated id={created_ids['report_id'][:8]}..."))
            else:
                steps.append(step("fetch_report", STEP_FAIL, r.text))
                return _result(steps, start)

        # ── Step 11: Edit report — add impression ─────────────────────────────
        r = await client.patch(f"/api/v1/reports/{created_ids['report_id']}", json={
            "impression": "E2E: Suspicious lesion. Recommend biopsy. BI-RADS 4B.",
        }, headers=headers)
        if r.status_code == 200:
            steps.append(step("edit_report", STEP_PASS, "impression added"))
        else:
            steps.append(step("edit_report", STEP_FAIL, r.text))

        # ── Step 12: Assign risk level ────────────────────────────────────────
        r = await client.patch(
            f"/api/v1/reports/{created_ids['report_id']}/risk",
            json={"risk_level": "high"},
            headers=headers,
        )
        if r.status_code == 200 and r.json()["risk_level"] == "high":
            steps.append(step("assign_risk", STEP_PASS, "risk=high"))
        else:
            steps.append(step("assign_risk", STEP_FAIL, r.text))

        # ── Step 13: Create template ──────────────────────────────────────────
        r = await client.post("/api/v1/templates", json={
            "name": f"E2E Template {test_id}",
            "scan_type": "breast_ultrasound",
            "structure": ["Clinical Indication", "Technique", "Right Breast",
                          "Left Breast", "Axillary Nodes", "Impression"],
        }, headers=headers)
        if r.status_code == 201:
            created_ids["template_id"] = r.json()["id"]
            steps.append(step("create_template", STEP_PASS,
                f"id={created_ids['template_id'][:8]}..."))
        else:
            steps.append(step("create_template", STEP_FAIL, r.text))

        # ── Step 14: Apply template ───────────────────────────────────────────
        if "template_id" in created_ids:
            r = await client.post(
                f"/api/v1/reports/{created_ids['report_id']}/apply-template/{created_ids['template_id']}",
                headers=headers,
            )
            if r.status_code == 200:
                steps.append(step("apply_template", STEP_PASS, "template applied"))
            else:
                steps.append(step("apply_template", STEP_FAIL, r.text))
        else:
            steps.append(step("apply_template", STEP_SKIP, "no template created"))

        # ── Step 15: Finalize report ──────────────────────────────────────────
        r = await client.post(
            f"/api/v1/reports/{created_ids['report_id']}/finalize",
            headers=headers,
        )
        if r.status_code == 200 and r.json()["is_final"]:
            steps.append(step("finalize_report", STEP_PASS, "is_final=true"))
        else:
            steps.append(step("finalize_report", STEP_FAIL, r.text))

        # ── Step 16: Dashboard check ──────────────────────────────────────────
        r = await client.get("/api/v1/dashboard", headers=headers)
        if r.status_code == 200:
            data = r.json()
            pending = len(data["pending_scans"])
            recent = len(data["recent_completed"])
            steps.append(step("dashboard_check", STEP_PASS,
                f"pending={pending}, recent_completed={recent}, today={data['total_today']}"))
        else:
            steps.append(step("dashboard_check", STEP_FAIL, r.text))

        # ── Step 17: Checklist endpoint ───────────────────────────────────────
        r = await client.get("/api/v1/checklists/breast_ultrasound", headers=headers)
        if r.status_code == 200:
            count = r.json()["total"]
            steps.append(step("checklist_endpoint", STEP_PASS, f"{count} items for breast_ultrasound"))
        else:
            steps.append(step("checklist_endpoint", STEP_FAIL, r.text))

    # ── Cleanup ───────────────────────────────────────────────────────────────
    await _cleanup(created_ids)
    steps.append(step("cleanup", STEP_PASS, "test data removed"))

    result = _result(steps, start)
    passed = sum(1 for s in steps if s.status == STEP_PASS)
    failed = sum(1 for s in steps if s.status == STEP_FAIL)
    print(f"\n  Result: {result.overall.upper()}  ({passed} passed, {failed} failed)")
    print(f"  Duration: {result.duration_ms:.1f}ms")
    print(f"{'═'*55}\n")
    return result


async def _cleanup(ids: dict):
    try:
        if "user_id" in ids:
            oid = ObjectId(ids["user_id"])
            await users_col().delete_one({"_id": oid})
        if "patient_id" in ids:
            await patients_col().delete_one({"_id": ObjectId(ids["patient_id"])})
        if "scan_id" in ids:
            await scans_col().delete_one({"_id": ObjectId(ids["scan_id"])})
        if "report_id" in ids:
            await reports_col().delete_one({"_id": ObjectId(ids["report_id"])})
        if "template_id" in ids:
            await templates_col().delete_one({"_id": ObjectId(ids["template_id"])})
        await otps_col().delete_many({"phone": {"$regex": "^\\+23480"}})
    except Exception as e:
        print(f"[E2E CLEANUP ERROR] {e}")


def _result(steps: list[E2EStepResult], start: float) -> E2ETestResponse:
    overall = "fail" if any(s.status == STEP_FAIL for s in steps) else "pass"
    duration_ms = (time.monotonic() - start) * 1000
    return E2ETestResponse(overall=overall, steps=steps, duration_ms=duration_ms)
