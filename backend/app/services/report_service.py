
from datetime import datetime, timezone

REPORT_TEMPLATES = {
    "breast_ultrasound": {
        "sections": ["Clinical Indication", "Technique", "Findings", "Impression"],
        "default_technique": "Real-time grey-scale ultrasound of both breasts was performed.",
    },
    "fetal_ultrasound": {
        "sections": ["Clinical Indication", "Technique", "Biometry", "Findings", "Impression"],
        "default_technique": "Transabdominal ultrasound was performed.",
    },
    "chest_xray": {
        "sections": ["Clinical Indication", "Technique", "Findings", "Impression"],
        "default_technique": "PA chest radiograph was obtained.",
    },
    "abdominal_ultrasound": {
        "sections": ["Clinical Indication", "Technique", "Findings", "Impression"],
        "default_technique": "Real-time grey-scale abdominal ultrasound was performed.",
    },
    "pelvic_ultrasound": {
        "sections": ["Clinical Indication", "Technique", "Findings", "Impression"],
        "default_technique": "Transabdominal pelvic ultrasound was performed.",
    },
}


def _checklist_to_findings_notes(checklist: list[dict]) -> str:
    """Converts completed checklist items into a structured findings note."""
    completed = [item for item in checklist if item.get("completed")]
    if not completed:
        return ""
    lines = []
    for item in completed:
        val = item.get("value")
        if val:
            lines.append(f"• {item['label']}: {val}")
        else:
            lines.append(f"• {item['label']}: ✓")
    return "\n".join(lines)


def _ai_flags_summary(ai_flags: list[dict]) -> str:
    """Summarise AI events that were flagged during the scan."""
    abnormal = [f for f in ai_flags if f.get("event_type") == "possible_abnormality"]
    if not abnormal:
        return ""
    lines = ["--- AI Flagged Events ---"]
    for event in abnormal:
        ts = event.get("timestamp_seconds", 0)
        lines.append(f"• t={ts}s: {event['message']}")
    return "\n".join(lines)


def generate_report_document(
    scan: dict,
    patient: dict,
    radiologist_name: str,
    media_urls: list[str] | None = None,
) -> dict:
    """
    Builds a full structured report dict from scan session data.
    media_urls: optional list of URLs from the media collection
                (overrides scan.captured_frames if provided)
    """
    scan_type = scan.get("scan_type", "")
    template_meta = REPORT_TEMPLATES.get(scan_type, {})
    technique = template_meta.get("default_technique", "Ultrasound examination was performed.")

    transcript = scan.get("transcript", "").strip()
    checklist = scan.get("checklist", [])
    ai_flags = scan.get("ai_flags", [])

    checklist_notes = _checklist_to_findings_notes(checklist)
    ai_summary = _ai_flags_summary(ai_flags)

    # Combine transcript + checklist + AI summary into findings
    findings_parts = []
    if transcript:
        findings_parts.append(transcript)
    if checklist_notes:
        findings_parts.append("\n--- Checklist Summary ---\n" + checklist_notes)
    if ai_summary:
        findings_parts.append("\n" + ai_summary)
    findings = "\n\n".join(findings_parts) if findings_parts else "Findings to be completed by radiologist."

    # Use provided media_urls if given, otherwise fall back to captured_frames on scan doc
    if media_urls is not None:
        frame_urls = media_urls
    else:
        frame_urls = [f["url"] for f in scan.get("captured_frames", [])]

    now = datetime.now(timezone.utc)

    return {
        "scan_id": str(scan["_id"]),
        "patient_id": str(scan["patient_id"]),
        "patient_name": patient.get("name", "Unknown"),
        "patient_age": patient.get("age"),
        "patient_sex": patient.get("sex"),
        "scan_type": scan_type,
        "clinical_indication": scan.get("clinical_indication", ""),
        "technique": technique,
        "findings": findings,
        "impression": "",           # Radiologist fills this in the editor
        "risk_level": None,
        "template_id": None,
        "captured_frame_urls": frame_urls,
        "is_final": False,
        "created_by": str(scan["created_by"]),
        "radiologist_name": radiologist_name,
        "created_at": now,
        "updated_at": now,
        "finalised_at": None,
    }
