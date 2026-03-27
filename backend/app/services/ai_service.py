
from datetime import datetime, timezone


AI_EVENT_RULES: dict[str, list[tuple]] = {
    "breast_ultrasound": [
        (5,  "info",                "Scan started. Begin with right breast"),
        (8,  "possible_abnormality","Hypoechoic region detected — verify margins"),
        (14, "good_frame",          "Good frame — consider capturing"),
        (20, "consider_capture",    "Measure lesion dimensions now"),
        (28, "possible_abnormality","Posterior acoustic shadowing noted"),
        (35, "info",                "Transition to left breast"),
        (42, "good_frame",          "Good frame — axillary region visible"),
        (50, "info",                "Checklist: confirm BI-RADS category before completing"),
    ],
    "fetal_ultrasound": [
        (6,  "info",                "Begin with fetal cardiac activity check"),
        (10, "good_frame",          "Good cephalic view — measure BPD and HC"),
        (18, "consider_capture",    "Capture abdominal circumference view"),
        (25, "good_frame",          "Good femur view — measure FL"),
        (32, "info",                "Assess amniotic fluid index"),
        (40, "possible_abnormality","Fluid level appears reduced — verify"),
        (48, "good_frame",          "Good placenta view — document location"),
        (55, "info",                "Complete anatomy survey before finishing"),
    ],
    "chest_xray": [
        (4,  "info",                "Evaluate lung fields systematically — start right"),
        (8,  "possible_abnormality","Opacity in right lower zone — review"),
        (12, "good_frame",          "Good cardiac silhouette view — document"),
        (18, "info",                "Check costophrenic angles for effusion"),
        (24, "consider_capture",    "Capture final frame for report"),
    ],
    "abdominal_ultrasound": [
        (5,  "info",                "Start with liver — assess size and echotexture"),
        (12, "possible_abnormality","Gallbladder wall thickening noted — verify"),
        (20, "good_frame",          "Good right kidney view — measure"),
        (28, "consider_capture",    "Capture left kidney view"),
        (35, "info",                "Check for free fluid in Morrison's pouch"),
    ],
    "pelvic_ultrasound": [
        (5,  "info",                "Begin with uterus — document size and position"),
        (12, "good_frame",          "Good endometrial view — measure thickness"),
        (18, "possible_abnormality","Adnexal region appears abnormal — assess"),
        (25, "consider_capture",    "Capture right ovary view with measurements"),
        (32, "good_frame",          "Good left ovary view"),
        (38, "info",                "Assess for free fluid in Pouch of Douglas"),
    ],
}


def get_ai_events_for_scan(scan_type: str, elapsed_seconds: float | None = None) -> list[dict]:
    """
    Returns all AI events for a scan type.
    If elapsed_seconds is provided, returns only events up to that timestamp
    (simulates real-time delivery during an active scan).
    """
    rules = AI_EVENT_RULES.get(scan_type, [])
    now = datetime.now(timezone.utc)

    events = []
    for ts, event_type, message in rules:
        if elapsed_seconds is not None and ts > elapsed_seconds:
            continue
        events.append({
            "timestamp_seconds": ts,
            "event_type": event_type,
            "message": message,
            "frame_url": None,
            "acknowledged": False,
        })
    return events
