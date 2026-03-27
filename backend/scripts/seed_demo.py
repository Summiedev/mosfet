"""
Seed RadFlow demo database — covers every screen in the UI.
Usage:  python scripts/seed_demo.py

Screens covered
───────────────
  Login            → demo@radflow.com / radflow123
  OTP              → pre-verified (otp_verified=True), phone +2348012345678
  Dashboard        → Waiting 3 | In Progress 1 | Completed Today 2
                     Active workload card: Sarah Jenkins (Low Risk, pending)
                     Recently completed table: Grace Okafor (HIGH) + Emeka Nwosu (MODERATE)
  Start New Scan   → (live — user fills in from UI)
  Scan View        → Amaka Johnson — Breast US — IN-PROGRESS
                       • Live voice transcript lines
                       • 3 captured frames (UOQ / UIQ / LOQ)
                       • Anatomical map: UOQ finding (red X) + UIQ + LOQ green
                       • Protocol checklist: 4/11 items completed
                       • AI flags at various timestamps
                       • Bottom AI toast: "Possible abnormality in upper outer quadrant"
  Review Capture   → captured frame for Amaka — AI Detection bar 87%
  Review & Finalize→ Breast Ultrasound Report for Amaka (Draft)
                       Full structured findings + impression + recommendation
  Report Sent      → Grace Okafor finalised report (is_final=True)

Credentials
───────────
  Email   : demo@radflow.com
  Password: radflow123
  Role    : hybrid (full access)
"""

import asyncio
import os
import sys
from datetime import datetime, timedelta, timezone

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.core.config import settings
from app.services.checklist_service import get_checklist, CHECKLISTS
from app.services.ai_service import get_ai_events_for_scan

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

IMAGES = {
    "breast_mass":
        "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3b/"
        "Breast_fibroadenoma_2.jpg/400px-Breast_fibroadenoma_2.jpg",
    "breast_normal":
        "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e1/"
        "Breast_normal_ultrasound.jpg/400px-Breast_normal_ultrasound.jpg",
    "fetal_bpd":
        "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9e/"
        "Fetal_Ultrasound_BPD.jpg/400px-Fetal_Ultrasound_BPD.jpg",
    "fetal_face":
        "https://upload.wikimedia.org/wikipedia/commons/thumb/2/27/"
        "Fetal_Ultrasound_%283D%29.jpg/400px-Fetal_Ultrasound_%283D%29.jpg",
    "chest_tb":
        "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3e/"
        "TB_CXR.jpg/400px-TB_CXR.jpg",
    "chest_normal":
        "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/"
        "Normal_posteroanterior_%28PA%29_chest_radiograph_%28X-ray%29.jpg/"
        "400px-Normal_posteroanterior_%28PA%29_chest_radiograph_%28X-ray%29.jpg",
    "abdomen_gallstone":
        "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/"
        "Gallstones_ultrasound_2.jpg/400px-Gallstones_ultrasound_2.jpg",
    "abdomen_liver":
        "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b5/"
        "Abdomen_ultrasound_%28cropped%29.jpg/400px-Abdomen_ultrasound_%28cropped%29.jpg",
}


def full_checklist(scan_type):
    return [{**item, "completed": True} for item in get_checklist(scan_type)]


def partial_checklist(scan_type, completed_keys):
    items = get_checklist(scan_type)
    for item in items:
        item["completed"] = item["key"] in completed_keys
    return items


SCAN_VIEW_PARTIAL_KEYS = {
    "clinical_indication",
    "right_breast",
    "lesion_size",
    "lesion_location",
}


async def seed():
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB_NAME]

    print("Seeding RadFlow demo database (full-screen coverage)...")

    for col in ["users", "patients", "scans", "reports",
                "templates", "otps", "media", "checklist_configs"]:
        await db[col].delete_many({})
    print("  Cleared existing collections")

    now = datetime.now(timezone.utc)

    # ── 1. DEMO USER
    user_id = ObjectId()
    await db["users"].insert_one({
        "_id": user_id,
        "full_name": "Dr. Roberts",
        "email": "demo@radflow.com",
        "phone": "+2348012345678",
        "password_hash": pwd_context.hash("radflow123"),
        "role": "hybrid",
        "otp_verified": True,
        "is_active": True,
        "created_at": now,
        "updated_at": now,
    })
    print("  + Demo user: demo@radflow.com / radflow123  (hybrid, otp_verified)")

    # ── 2. PATIENTS
    p_amaka = ObjectId()
    p_grace = ObjectId()
    p_emeka = ObjectId()
    p_funke = ObjectId()
    p_sarah = ObjectId()

    await db["patients"].insert_many([
        {"_id": p_amaka,  "name": "Amaka Johnson", "age": 34, "sex": "female",
         "phone": "+2348023000001", "created_by": user_id,
         "created_at": now - timedelta(minutes=60), "updated_at": now - timedelta(minutes=60)},
        {"_id": p_grace,  "name": "Grace Okafor",  "age": 29, "sex": "female",
         "phone": "+2348023000002", "created_by": user_id,
         "created_at": now - timedelta(hours=3),   "updated_at": now - timedelta(hours=3)},
        {"_id": p_emeka,  "name": "Emeka Nwosu",   "age": 55, "sex": "male",
         "phone": "+2348023000003", "created_by": user_id,
         "created_at": now - timedelta(hours=5),   "updated_at": now - timedelta(hours=5)},
        {"_id": p_funke,  "name": "Funke Adeyemi", "age": 38, "sex": "female",
         "phone": "+2348023000004", "created_by": user_id,
         "created_at": now - timedelta(minutes=20), "updated_at": now - timedelta(minutes=20)},
        {"_id": p_sarah,  "name": "Sarah Jenkins",  "age": 42, "sex": "female",
         "phone": "+2348023000005", "created_by": user_id,
         "created_at": now - timedelta(minutes=10), "updated_at": now - timedelta(minutes=10)},
    ])
    print("  + 5 patients")

    # ── 3. SCAN — AMAKA JOHNSON (IN-PROGRESS) → Scan View + Review Capture + Review & Finalize
    s_amaka = ObjectId()
    amaka_checklist = partial_checklist("breast_ultrasound", SCAN_VIEW_PARTIAL_KEYS)

    amaka_frames = [
        {"url": IMAGES["breast_mass"],   "captured_at": now - timedelta(minutes=18),
         "ai_suggested": True,  "note": "UOQ — Hypoechoic mass detected",   "anatomical_region": "UOQ"},
        {"url": IMAGES["breast_normal"], "captured_at": now - timedelta(minutes=12),
         "ai_suggested": False, "note": "UIQ — No lesion identified",        "anatomical_region": "UIQ"},
        {"url": IMAGES["abdomen_liver"], "captured_at": now - timedelta(minutes=8),
         "ai_suggested": False, "note": "LOQ — Lower outer quadrant view",   "anatomical_region": "LOQ"},
    ]

    amaka_transcript = (
        "08:13  Scanning right breast, starting from the nipple and moving outward.\n"
        "08:31  There is a hypoechoic mass in the upper outer quadrant, "
        "measuring approximately 1.5 cm.\n"
        "08:45  Margins appear irregular. Posterior acoustic shadowing present.\n"
        "08:58  Moving to the upper inner quadrant — no lesion identified.\n"
        "09:12  Lower outer quadrant appears normal. No adenopathy in axilla."
    )

    await db["scans"].insert_one({
        "_id": s_amaka,
        "patient_id": p_amaka,
        "scan_type": "breast_ultrasound",
        "clinical_indication": "Palpable lump in left breast — noticed 2 months ago",
        "status": "in_progress",
        "checklist": amaka_checklist,
        "transcript": amaka_transcript,
        "captured_frames": amaka_frames,
        "ai_flags": get_ai_events_for_scan("breast_ultrasound", elapsed_seconds=35),
        "created_by": user_id,
        "created_at": now - timedelta(minutes=60),
        "updated_at": now - timedelta(minutes=3),
        "completed_at": None,
    })
    print("  + Scan — Amaka Johnson (breast US, in-progress, 3 captures, 4/11 checklist)")

    # Draft report for Amaka — Review & Finalize screen (is_final=False)
    r_amaka = ObjectId()
    await db["reports"].insert_one({
        "_id": r_amaka,
        "scan_id": str(s_amaka),
        "patient_id": str(p_amaka),
        "patient_name": "Amaka Johnson",
        "patient_age": 34,
        "patient_sex": "female",
        "scan_type": "breast_ultrasound",
        "clinical_indication": "Palpable lump in left breast — noticed 2 months ago",
        "technique": (
            "Real-time grey-scale ultrasound of both breasts performed "
            "using a high-frequency linear probe."
        ),
        "findings": (
            "RIGHT BREAST:\n"
            "  Upper Outer Quadrant (UOQ): Hypoechoic solid mass measuring 1.5 x 1.2 cm.\n"
            "  Margins: Irregular. Posterior features: Acoustic shadowing present.\n"
            "  No skin thickening or nipple retraction.\n\n"
            "  Upper Inner Quadrant: No focal lesion identified.\n"
            "  Lower quadrants: Normal parenchymal echotexture.\n\n"
            "LEFT BREAST:\n"
            "  No focal mass, cyst, or abnormal lymph node identified.\n\n"
            "AXILLARY LYMPH NODES:\n"
            "  Right axilla: Single borderline node, 12 mm short axis — indeterminate.\n"
            "  Left axilla: Normal."
        ),
        "impression": (
            "Right breast UOQ hypoechoic mass (1.5 cm) with irregular margins and "
            "posterior acoustic shadowing. "
            "Appearances are suspicious — BI-RADS 4B. "
            "Core needle biopsy recommended for histological diagnosis."
        ),
        "recommendation": "Core needle biopsy. Refer to breast surgery.",
        "risk_level": "high",
        "birads": "4B",
        "template_id": None,
        "captured_frame_urls": [f["url"] for f in amaka_frames],
        "is_final": False,
        "created_by": str(user_id),
        "radiologist_name": "Dr. K. Roberts",
        "created_at": now - timedelta(minutes=5),
        "updated_at": now - timedelta(minutes=2),
        "finalised_at": None,
    })
    print("  + Report — Amaka Johnson (Draft, BI-RADS 4B, HIGH risk)")

    # ── 4. SCAN — GRACE OKAFOR (FINALISED) → Report Sent screen
    s_grace    = ObjectId()
    grace_done = now - timedelta(minutes=45)

    await db["scans"].insert_one({
        "_id": s_grace,
        "patient_id": p_grace,
        "scan_type": "fetal_ultrasound",
        "clinical_indication": "Routine check — 20 weeks",
        "status": "completed",
        "checklist": full_checklist("fetal_ultrasound"),
        "transcript": (
            "Single live intrauterine fetus, cephalic presentation. "
            "GA by biometry 20w2d. FHR 152 bpm. "
            "BPD 49 mm, HC 181 mm, AC 162 mm, FL 33 mm. "
            "EFW 345 g — below 10th centile, query IUGR. "
            "AFI 6 cm — borderline low. "
            "Placenta posterior, upper segment, clear of os. "
            "Umbilical artery Doppler: increased resistance, absent end-diastolic flow."
        ),
        "captured_frames": [
            {"url": IMAGES["fetal_bpd"],  "captured_at": grace_done - timedelta(minutes=20),
             "ai_suggested": True,  "note": "BPD measurement — 49 mm", "anatomical_region": None},
            {"url": IMAGES["fetal_face"], "captured_at": grace_done - timedelta(minutes=10),
             "ai_suggested": False, "note": "Fetal face — anatomy survey", "anatomical_region": None},
        ],
        "ai_flags": get_ai_events_for_scan("fetal_ultrasound"),
        "created_by": user_id,
        "created_at": now - timedelta(hours=2),
        "updated_at": grace_done,
        "completed_at": grace_done,
    })

    await db["reports"].insert_one({
        "scan_id": str(s_grace),
        "patient_id": str(p_grace),
        "patient_name": "Grace Okafor",
        "patient_age": 29,
        "patient_sex": "female",
        "scan_type": "fetal_ultrasound",
        "clinical_indication": "Routine check — 20 weeks",
        "technique": "Transabdominal ultrasound performed using a curvilinear probe.",
        "findings": (
            "Single live intrauterine fetus in cephalic presentation.\n\n"
            "Gestational Age: 20 weeks 2 days (biometry), consistent with LMP.\n\n"
            "Cardiac Activity: Present and regular — FHR 152 bpm.\n\n"
            "Biometry:\n"
            "  BPD  49 mm\n"
            "  HC   181 mm\n"
            "  AC   162 mm\n"
            "  FL   33 mm\n"
            "  EFW  345 g — below 10th centile. Query IUGR.\n\n"
            "Amniotic Fluid: AFI 6 cm — borderline low. Query oligohydramnios.\n\n"
            "Placenta: Posterior, upper segment, clear of internal os.\n\n"
            "Anatomy Survey: No structural anomaly identified.\n\n"
            "Umbilical Artery Doppler: Increased resistance, absent end-diastolic flow."
        ),
        "impression": (
            "Fetal growth restriction (EFW <10th centile) with borderline oligohydramnios "
            "and abnormal umbilical artery Doppler. "
            "Urgent obstetric review recommended. "
            "Repeat growth scan in 2 weeks."
        ),
        "recommendation": "Urgent obstetric referral. Repeat scan in 2 weeks.",
        "risk_level": "high",
        "template_id": None,
        "captured_frame_urls": [IMAGES["fetal_bpd"], IMAGES["fetal_face"]],
        "is_final": True,
        "created_by": str(user_id),
        "radiologist_name": "Dr. Roberts",
        "created_at": grace_done,
        "updated_at": grace_done + timedelta(minutes=12),
        "finalised_at": grace_done + timedelta(minutes=12),
    })
    print("  + Scan + Report — Grace Okafor (fetal US, FINALISED, HIGH risk)")

    # ── 5. SCAN — EMEKA NWOSU (FINALISED) → Recently Completed table
    s_emeka    = ObjectId()
    emeka_done = now - timedelta(hours=1, minutes=30)

    await db["scans"].insert_one({
        "_id": s_emeka,
        "patient_id": p_emeka,
        "scan_type": "chest_xray",
        "clinical_indication": "Productive cough 3 weeks, fever, night sweats — query PTB",
        "status": "completed",
        "checklist": full_checklist("chest_xray"),
        "transcript": (
            "PA chest radiograph. "
            "Right upper lobe opacity with ill-defined margins. "
            "No pleural effusion. Cardiac silhouette normal size. "
            "Mediastinum not widened. Left lung clear."
        ),
        "captured_frames": [
            {"url": IMAGES["chest_tb"],     "captured_at": emeka_done - timedelta(minutes=5),
             "ai_suggested": True,  "note": "RUL opacity — possible consolidation", "anatomical_region": None},
            {"url": IMAGES["chest_normal"], "captured_at": emeka_done - timedelta(minutes=2),
             "ai_suggested": False, "note": "Left lung — clear", "anatomical_region": None},
        ],
        "ai_flags": get_ai_events_for_scan("chest_xray"),
        "created_by": user_id,
        "created_at": now - timedelta(hours=2, minutes=30),
        "updated_at": emeka_done,
        "completed_at": emeka_done,
    })

    await db["reports"].insert_one({
        "scan_id": str(s_emeka),
        "patient_id": str(p_emeka),
        "patient_name": "Emeka Nwosu",
        "patient_age": 55,
        "patient_sex": "male",
        "scan_type": "chest_xray",
        "clinical_indication": "Productive cough 3 weeks, fever, night sweats — query PTB",
        "technique": "PA chest radiograph obtained in full inspiration.",
        "findings": (
            "Lung Fields: Right upper lobe — ill-defined homogeneous opacity. Left lung clear.\n\n"
            "Cardiac Silhouette: Normal size and contour.\n\n"
            "Mediastinum: Not widened. Trachea central.\n\n"
            "Pleura: No pleural effusion or pneumothorax.\n\n"
            "Diaphragm: Both domes normal. Costophrenic angles clear.\n\n"
            "Bones: No lytic or sclerotic lesion."
        ),
        "impression": (
            "Right upper lobe opacity consistent with pulmonary tuberculosis. "
            "Sputum AFB smear and GeneXpert recommended. "
            "Refer to respiratory medicine."
        ),
        "recommendation": "Sputum AFB + GeneXpert. Respiratory medicine referral.",
        "risk_level": "moderate",
        "template_id": None,
        "captured_frame_urls": [IMAGES["chest_tb"], IMAGES["chest_normal"]],
        "is_final": True,
        "created_by": str(user_id),
        "radiologist_name": "Dr. Roberts",
        "created_at": emeka_done,
        "updated_at": emeka_done + timedelta(minutes=10),
        "finalised_at": emeka_done + timedelta(minutes=10),
    })
    print("  + Scan + Report — Emeka Nwosu (chest XR, FINALISED, MODERATE risk)")

    # ── 6. SCAN — FUNKE ADEYEMI (PENDING) → Waiting counter
    s_funke = ObjectId()
    await db["scans"].insert_one({
        "_id": s_funke,
        "patient_id": p_funke,
        "scan_type": "abdominal_ultrasound",
        "clinical_indication": "Right upper quadrant pain — query gallstones",
        "status": "pending",
        "checklist": get_checklist("abdominal_ultrasound"),
        "transcript": "",
        "captured_frames": [],
        "ai_flags": [],
        "created_by": user_id,
        "created_at": now - timedelta(minutes=20),
        "updated_at": now - timedelta(minutes=20),
        "completed_at": None,
    })
    print("  + Scan — Funke Adeyemi (abdominal US, pending)")

    # ── 7. SCAN — SARAH JENKINS (PENDING) → Active Workload card (Low Risk)
    s_sarah = ObjectId()
    await db["scans"].insert_one({
        "_id": s_sarah,
        "patient_id": p_sarah,
        "scan_type": "breast_ultrasound",
        "clinical_indication": "Follow-up on previously noted right breast cyst",
        "status": "pending",
        "checklist": get_checklist("breast_ultrasound"),
        "transcript": "",
        "captured_frames": [],
        "ai_flags": [],
        "created_by": user_id,
        "created_at": now - timedelta(minutes=10),
        "updated_at": now - timedelta(minutes=10),
        "completed_at": None,
    })

    await db["reports"].insert_one({
        "scan_id": str(s_sarah),
        "patient_id": str(p_sarah),
        "patient_name": "Sarah Jenkins",
        "patient_age": 42,
        "patient_sex": "female",
        "scan_type": "breast_ultrasound",
        "clinical_indication": "Follow-up on previously noted right breast cyst",
        "technique": (
            "Real-time grey-scale ultrasound of both breasts performed "
            "using a high-frequency linear probe."
        ),
        "findings": "Simple cyst right breast, stable since previous scan. No new lesion.",
        "impression": "Stable simple cyst — likely benign. BI-RADS 2.",
        "recommendation": "Routine annual follow-up.",
        "risk_level": "low",
        "birads": "2",
        "template_id": None,
        "captured_frame_urls": [],
        "is_final": False,
        "created_by": str(user_id),
        "radiologist_name": "Dr. Roberts",
        "created_at": now - timedelta(minutes=9),
        "updated_at": now - timedelta(minutes=9),
        "finalised_at": None,
    })
    print("  + Scan + Report — Sarah Jenkins (breast US, pending, LOW risk draft)")

    # ── 8. MEDIA
    await db["media"].insert_many([
        {"scan_id": str(s_amaka), "patient_id": str(p_amaka),
         "url": IMAGES["breast_mass"],   "public_id": "radflow/frames/amaka_uoq_001",
         "filename": "breast_uoq_mass.jpg",   "mime_type": "image/jpeg",
         "size_bytes": 98_432, "width": 400, "height": 335,
         "ai_suggested": True,  "ai_event_type": "possible_abnormality", "ai_confidence": 0.87,
         "anatomical_region": "UOQ", "note": "Hypoechoic mass — upper outer quadrant",
         "uploaded_by": str(user_id), "uploaded_at": now - timedelta(minutes=18)},

        {"scan_id": str(s_amaka), "patient_id": str(p_amaka),
         "url": IMAGES["breast_normal"], "public_id": "radflow/frames/amaka_uiq_001",
         "filename": "breast_uiq_normal.jpg", "mime_type": "image/jpeg",
         "size_bytes": 74_816, "width": 400, "height": 350,
         "ai_suggested": False, "ai_event_type": None, "ai_confidence": None,
         "anatomical_region": "UIQ", "note": "Upper inner quadrant — normal",
         "uploaded_by": str(user_id), "uploaded_at": now - timedelta(minutes=12)},

        {"scan_id": str(s_amaka), "patient_id": str(p_amaka),
         "url": IMAGES["abdomen_liver"], "public_id": "radflow/frames/amaka_loq_001",
         "filename": "breast_loq_view.jpg",   "mime_type": "image/jpeg",
         "size_bytes": 81_920, "width": 400, "height": 320,
         "ai_suggested": False, "ai_event_type": None, "ai_confidence": None,
         "anatomical_region": "LOQ", "note": "Lower outer quadrant — no lesion",
         "uploaded_by": str(user_id), "uploaded_at": now - timedelta(minutes=8)},

        {"scan_id": str(s_grace), "patient_id": str(p_grace),
         "url": IMAGES["fetal_bpd"],  "public_id": "radflow/frames/grace_bpd_001",
         "filename": "fetal_bpd_49mm.jpg",    "mime_type": "image/jpeg",
         "size_bytes": 88_064, "width": 400, "height": 320,
         "ai_suggested": True, "ai_event_type": "good_frame", "ai_confidence": 0.92,
         "anatomical_region": None, "note": "BPD measurement — 49 mm",
         "uploaded_by": str(user_id), "uploaded_at": grace_done - timedelta(minutes=20)},

        {"scan_id": str(s_grace), "patient_id": str(p_grace),
         "url": IMAGES["fetal_face"], "public_id": "radflow/frames/grace_face_001",
         "filename": "fetal_face_anatomy.jpg", "mime_type": "image/jpeg",
         "size_bytes": 102_400, "width": 400, "height": 400,
         "ai_suggested": False, "ai_event_type": None, "ai_confidence": None,
         "anatomical_region": None, "note": "Fetal face — anatomy survey",
         "uploaded_by": str(user_id), "uploaded_at": grace_done - timedelta(minutes=10)},

        {"scan_id": str(s_emeka), "patient_id": str(p_emeka),
         "url": IMAGES["chest_tb"],   "public_id": "radflow/frames/emeka_chest_001",
         "filename": "chest_rul_opacity.jpg",  "mime_type": "image/jpeg",
         "size_bytes": 115_712, "width": 400, "height": 453,
         "ai_suggested": True, "ai_event_type": "possible_abnormality", "ai_confidence": 0.79,
         "anatomical_region": None, "note": "RUL opacity — possible PTB",
         "uploaded_by": str(user_id), "uploaded_at": emeka_done - timedelta(minutes=5)},

        {"scan_id": str(s_emeka), "patient_id": str(p_emeka),
         "url": IMAGES["chest_normal"], "public_id": "radflow/frames/emeka_chest_002",
         "filename": "chest_left_clear.jpg",   "mime_type": "image/jpeg",
         "size_bytes": 89_088, "width": 400, "height": 449,
         "ai_suggested": False, "ai_event_type": None, "ai_confidence": None,
         "anatomical_region": None, "note": "Left lung — clear",
         "uploaded_by": str(user_id), "uploaded_at": emeka_done - timedelta(minutes=3)},

        {"scan_id": str(s_funke), "patient_id": str(p_funke),
         "url": IMAGES["abdomen_gallstone"], "public_id": "radflow/frames/funke_gallstone_ref",
         "filename": "abdomen_gallstone.jpg", "mime_type": "image/jpeg",
         "size_bytes": 76_800, "width": 400, "height": 326,
         "ai_suggested": False, "ai_event_type": None, "ai_confidence": None,
         "anatomical_region": None, "note": "Gallstone reference image",
         "uploaded_by": str(user_id), "uploaded_at": now - timedelta(minutes=19)},
    ])
    print("  + 8 media items (ai_confidence + anatomical_region tagged)")

    # ── 9. TEMPLATES
    await db["templates"].insert_many([
        {"name": "Standard Breast Ultrasound", "scan_type": "breast_ultrasound",
         "structure": ["Clinical Indication", "Technique", "Right Breast", "Left Breast",
                       "Axillary Lymph Nodes", "Impression", "BI-RADS", "Recommendation"],
         "default_technique": (
             "Real-time grey-scale ultrasound of both breasts performed "
             "using a high-frequency linear probe."),
         "created_by": "global", "created_at": now},

        {"name": "Standard Obstetric Ultrasound", "scan_type": "fetal_ultrasound",
         "structure": ["Clinical Indication", "Technique", "Lie & Presentation",
                       "Cardiac Activity", "Biometry", "EFW", "Amniotic Fluid",
                       "Placenta", "Anatomy Survey", "Doppler", "Impression"],
         "default_technique": "Transabdominal ultrasound performed using a curvilinear probe.",
         "created_by": "global", "created_at": now},

        {"name": "Standard Chest X-Ray", "scan_type": "chest_xray",
         "structure": ["Clinical Indication", "Technique", "Lung Fields",
                       "Cardiac Silhouette", "Mediastinum", "Pleura",
                       "Diaphragm", "Bones", "Impression"],
         "default_technique": "PA chest radiograph obtained in full inspiration.",
         "created_by": "global", "created_at": now},

        {"name": "Standard Abdominal Ultrasound", "scan_type": "abdominal_ultrasound",
         "structure": ["Clinical Indication", "Technique", "Liver",
                       "Gallbladder & Bile Ducts", "Pancreas", "Spleen",
                       "Kidneys", "Aorta", "Free Fluid", "Impression"],
         "default_technique": "Transabdominal ultrasound performed after fasting.",
         "created_by": "global", "created_at": now},
    ])
    print("  + 4 global report templates")

    # ── 10. CHECKLIST CONFIGS
    for scan_type, items in CHECKLISTS.items():
        await db["checklist_configs"].insert_one({
            "_id": ObjectId(),
            "scan_type": scan_type,
            "items": items,
            "created_at": now,
        })
    print(f"  + {len(CHECKLISTS)} checklist configs")

    client.close()

    print("\n" + "=" * 60)
    print("  SEED COMPLETE")
    print("=" * 60)
    print()
    print("  Login          demo@radflow.com  /  radflow123")
    print("  Name           Dr. Roberts  (hybrid radiologist)")
    print()
    print("  DASHBOARD")
    print("    Waiting          3  (Amaka + Funke + Sarah)")
    print("    In Progress      1  (Amaka Johnson)")
    print("    Completed Today  2  (Grace + Emeka)")
    print("    Active Workload  Sarah Jenkins — Low Risk — pending")
    print("    Recently Completed:")
    print("      Grace Okafor   Fetal US   HIGH      Suspicious   Finalized")
    print("      Emeka Nwosu    Chest XR   MODERATE               Finalized")
    print()
    print("  SCAN VIEW  (Amaka Johnson)")
    print("    Status       in_progress")
    print("    Checklist    4 / 11 items ticked")
    print("    Transcript   5 timestamped voice lines")
    print("    Captures     3  (UOQ mass / UIQ normal / LOQ normal)")
    print("    AI flags     4  (breast US events up to 35 s)")
    print()
    print("  REVIEW CAPTURE  (Amaka — UOQ frame)")
    print("    ai_confidence  0.87  →  87% confidence bar")
    print("    ai_event_type  possible_abnormality  →  red AI Detection box")
    print()
    print("  REVIEW & FINALIZE  (Amaka — Draft)")
    print("    is_final       False  →  Status: Draft badge")
    print("    risk_level     high,  BI-RADS 4B")
    print("    Full findings + impression + recommendation pre-filled")
    print()
    print("  REPORT SENT  (Grace Okafor)")
    print("    is_final       True  →  Report Successfully Sent screen")
    print()
    print("  API docs  →  http://localhost:8000/docs")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(seed())