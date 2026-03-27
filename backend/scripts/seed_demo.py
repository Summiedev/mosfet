"""
Seed RadFlow demo database for hackathon presentation.
Usage:  python scripts/seed_demo.py

What this creates
─────────────────
Users   : 1 hybrid radiologist  (demo@radflow.com / radflow123)
Patients: 5  (mix of breast, fetal, chest, abdominal cases)
Scans   : 5  (1 in-progress · 2 finalised · 2 pending)
Reports : 2  finalised
Media   : 8  (real public ultrasound/x-ray images — no Cloudinary needed)
Templates: 3 global

Dashboard will show  →  Waiting: 3  |  In Progress: 1  |  Completed Today: 2
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

# ── Real public medical images (Wikipedia Commons — stable, no auth needed) ──
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


def partial_checklist(scan_type, n=3):
    items = get_checklist(scan_type)
    for i, item in enumerate(items):
        item["completed"] = i < n
    return items


async def seed():
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB_NAME]

    print("Seeding RadFlow demo database...")

    for col in ["users", "patients", "scans", "reports",
                "templates", "otps", "media", "checklist_configs"]:
        await db[col].delete_many({})
    print("  Cleared existing collections")

    now = datetime.now(timezone.utc)

    # ── Demo user ─────────────────────────────────────────────────────────────
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
    print("  + Demo user: demo@radflow.com / radflow123")

    # ── Patients ──────────────────────────────────────────────────────────────
    p1_id = ObjectId()
    p2_id = ObjectId()
    p3_id = ObjectId()
    p4_id = ObjectId()
    p5_id = ObjectId()

    await db["patients"].insert_many([
        {"_id": p1_id, "name": "Amaka Johnson",  "age": 34, "sex": "female",
         "phone": "+2348023000001", "created_by": user_id,
         "created_at": now - timedelta(minutes=30), "updated_at": now - timedelta(minutes=30)},
        {"_id": p2_id, "name": "Grace Okafor",   "age": 29, "sex": "female",
         "phone": "+2348023000002", "created_by": user_id,
         "created_at": now - timedelta(hours=3),  "updated_at": now - timedelta(hours=3)},
        {"_id": p3_id, "name": "Emeka Nwosu",    "age": 55, "sex": "male",
         "phone": "+2348023000003", "created_by": user_id,
         "created_at": now - timedelta(hours=5),  "updated_at": now - timedelta(hours=5)},
        {"_id": p4_id, "name": "Funke Adeyemi",  "age": 38, "sex": "female",
         "phone": "+2348023000004", "created_by": user_id,
         "created_at": now - timedelta(minutes=10), "updated_at": now - timedelta(minutes=10)},
        {"_id": p5_id, "name": "Sarah Jenkins",  "age": 42, "sex": "female",
         "phone": "+2348023000005", "created_by": user_id,
         "created_at": now - timedelta(minutes=10), "updated_at": now - timedelta(minutes=10)},
    ])
    print("  + 5 patients")

    # ── Scan 1 — Amaka Johnson · Breast US · IN-PROGRESS ─────────────────────
    # Active workload card on dashboard
    s1_id = ObjectId()
    await db["scans"].insert_one({
        "_id": s1_id,
        "patient_id": p1_id,
        "scan_type": "breast_ultrasound",
        "clinical_indication": "Palpable lump in left breast, noticed 2 months ago",
        "status": "in_progress",
        "checklist": partial_checklist("breast_ultrasound", n=2),
        "transcript": (
            "Scanning right breast... "
            "There is a hypoechoic mass in the upper outer quadrant, "
            "measuring approximately 1.5 cm."
        ),
        "captured_frames": [
            {
                "url": IMAGES["breast_mass"],
                "captured_at": now - timedelta(minutes=15),
                "ai_suggested": True,
                "note": "Possible hypoechoic area — UOQ",
            }
        ],
        "ai_flags": get_ai_events_for_scan("breast_ultrasound"),
        "created_by": user_id,
        "created_at": now - timedelta(minutes=30),
        "updated_at": now - timedelta(minutes=5),
        "completed_at": None,
    })
    print("  + Scan 1 — Amaka Johnson (breast US, in-progress)")

    # ── Scan 2 — Grace Okafor · Fetal US · COMPLETED + FINALISED (HIGH) ──────
    s2_id = ObjectId()
    s2_done = now - timedelta(minutes=45)

    await db["scans"].insert_one({
        "_id": s2_id,
        "patient_id": p2_id,
        "scan_type": "fetal_ultrasound",
        "clinical_indication": "Routine check — 20 weeks",
        "status": "completed",
        "checklist": full_checklist("fetal_ultrasound"),
        "transcript": (
            "Single live intrauterine fetus, cephalic presentation. "
            "GA by biometry: 20w2d, consistent with LMP. "
            "FHR 152 bpm, regular. "
            "BPD 49mm, HC 181mm, AC 162mm, FL 33mm. "
            "EFW 345g — below 10th centile, query IUGR. "
            "AFI 6cm — borderline low, query oligohydramnios. "
            "Placenta: posterior, upper segment, clear of os. "
            "Anatomy survey: No structural anomaly identified. "
            "Umbilical artery Doppler: increased resistance, absent end-diastolic flow."
        ),
        "captured_frames": [
            {"url": IMAGES["fetal_bpd"],  "captured_at": s2_done - timedelta(minutes=20),
             "ai_suggested": True,  "note": "BPD measurement — 49mm"},
            {"url": IMAGES["fetal_face"], "captured_at": s2_done - timedelta(minutes=10),
             "ai_suggested": False, "note": "Fetal face — anatomy survey"},
        ],
        "ai_flags": get_ai_events_for_scan("fetal_ultrasound"),
        "created_by": user_id,
        "created_at": now - timedelta(hours=2),
        "updated_at": s2_done,
        "completed_at": s2_done,
    })

    r2_id = ObjectId()
    await db["reports"].insert_one({
        "_id": r2_id,
        "scan_id": str(s2_id),
        "patient_id": str(p2_id),
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
            "  BPD  49mm\n"
            "  HC   181mm\n"
            "  AC   162mm\n"
            "  FL   33mm\n"
            "  EFW  345g — below 10th centile. Query IUGR.\n\n"
            "Amniotic Fluid: AFI 6cm — borderline low. Query oligohydramnios.\n\n"
            "Placenta: Posterior, upper segment, clear of internal os.\n\n"
            "Anatomy Survey: No structural anomaly identified.\n\n"
            "Umbilical Artery Doppler: Increased resistance with absent end-diastolic flow."
        ),
        "impression": (
            "Fetal growth restriction (EFW <10th centile) with borderline oligohydramnios "
            "and abnormal umbilical artery Doppler. "
            "Urgent obstetric review recommended. "
            "Repeat growth scan in 2 weeks."
        ),
        "risk_level": "high",
        "template_id": None,
        "captured_frame_urls": [IMAGES["fetal_bpd"], IMAGES["fetal_face"]],
        "is_final": True,
        "created_by": str(user_id),
        "radiologist_name": "Dr. Roberts",
        "created_at": s2_done,
        "updated_at": s2_done + timedelta(minutes=12),
        "finalised_at": s2_done + timedelta(minutes=12),
    })
    print("  + Scan 2 — Grace Okafor (fetal US, finalised, HIGH risk)")

    # ── Scan 3 — Emeka Nwosu · Chest XR · COMPLETED + FINALISED (MODERATE) ───
    s3_id = ObjectId()
    s3_done = now - timedelta(hours=1, minutes=30)

    await db["scans"].insert_one({
        "_id": s3_id,
        "patient_id": p3_id,
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
            {"url": IMAGES["chest_tb"], "captured_at": s3_done - timedelta(minutes=5),
             "ai_suggested": True, "note": "RUL opacity — possible consolidation"},
        ],
        "ai_flags": get_ai_events_for_scan("chest_xray"),
        "created_by": user_id,
        "created_at": now - timedelta(hours=2, minutes=30),
        "updated_at": s3_done,
        "completed_at": s3_done,
    })

    await db["reports"].insert_one({
        "scan_id": str(s3_id),
        "patient_id": str(p3_id),
        "patient_name": "Emeka Nwosu",
        "patient_age": 55,
        "patient_sex": "male",
        "scan_type": "chest_xray",
        "clinical_indication": "Productive cough 3 weeks, fever, night sweats — query PTB",
        "technique": "PA chest radiograph obtained in full inspiration.",
        "findings": (
            "Lung Fields: Right upper lobe — ill-defined homogeneous opacity. "
            "Left lung clear.\n\n"
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
        "risk_level": "moderate",
        "template_id": None,
        "captured_frame_urls": [IMAGES["chest_tb"]],
        "is_final": True,
        "created_by": str(user_id),
        "radiologist_name": "Dr. Roberts",
        "created_at": s3_done,
        "updated_at": s3_done + timedelta(minutes=10),
        "finalised_at": s3_done + timedelta(minutes=10),
    })
    print("  + Scan 3 — Emeka Nwosu (chest XR, finalised, MODERATE risk)")

    # ── Scan 4 — Funke Adeyemi · Abdominal US · PENDING ──────────────────────
    await db["scans"].insert_one({
        "patient_id": p4_id,
        "scan_type": "abdominal_ultrasound",
        "clinical_indication": "Right upper quadrant pain, query gallstones",
        "status": "pending",
        "checklist": get_checklist("abdominal_ultrasound"),
        "transcript": "",
        "captured_frames": [],
        "ai_flags": [],
        "created_by": user_id,
        "created_at": now - timedelta(minutes=8),
        "updated_at": now - timedelta(minutes=8),
        "completed_at": None,
    })
    print("  + Scan 4 — Funke Adeyemi (abdominal US, pending)")

    # ── Scan 5 — Sarah Jenkins · Breast US · PENDING ─────────────────────────
    await db["scans"].insert_one({
        "patient_id": p5_id,
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
    print("  + Scan 5 — Sarah Jenkins (breast US, pending)")

    # ── Media — 8 items (real images, anatomical_region tagged) ──────────────
    await db["media"].insert_many([
        # Amaka Johnson — in-progress breast (3 captures, different quadrants)
        {"scan_id": str(s1_id), "patient_id": str(p1_id),
         "url": IMAGES["breast_mass"],
         "public_id": "radflow/frames/amaka_uoq_001",
         "filename": "breast_uoq_mass.jpg", "mime_type": "image/jpeg",
         "size_bytes": 98_432, "width": 400, "height": 335,
         "ai_suggested": True, "ai_event_type": "possible_abnormality",
         "anatomical_region": "UOQ",
         "note": "Hypoechoic mass — upper outer quadrant",
         "uploaded_by": str(user_id), "uploaded_at": now - timedelta(minutes=15)},

        {"scan_id": str(s1_id), "patient_id": str(p1_id),
         "url": IMAGES["breast_normal"],
         "public_id": "radflow/frames/amaka_uiq_001",
         "filename": "breast_uiq_normal.jpg", "mime_type": "image/jpeg",
         "size_bytes": 74_816, "width": 400, "height": 350,
         "ai_suggested": False, "ai_event_type": None,
         "anatomical_region": "UIQ",
         "note": "Upper inner quadrant — normal",
         "uploaded_by": str(user_id), "uploaded_at": now - timedelta(minutes=10)},

        {"scan_id": str(s1_id), "patient_id": str(p1_id),
         "url": IMAGES["abdomen_liver"],
         "public_id": "radflow/frames/amaka_loq_001",
         "filename": "breast_loq_view.jpg", "mime_type": "image/jpeg",
         "size_bytes": 81_920, "width": 400, "height": 320,
         "ai_suggested": False, "ai_event_type": None,
         "anatomical_region": "LOQ",
         "note": "Lower outer quadrant — no lesion",
         "uploaded_by": str(user_id), "uploaded_at": now - timedelta(minutes=8)},

        # Grace Okafor — fetal (2 captures)
        {"scan_id": str(s2_id), "patient_id": str(p2_id),
         "url": IMAGES["fetal_bpd"],
         "public_id": "radflow/frames/grace_bpd_001",
         "filename": "fetal_bpd_49mm.jpg", "mime_type": "image/jpeg",
         "size_bytes": 88_064, "width": 400, "height": 320,
         "ai_suggested": True, "ai_event_type": "good_frame",
         "anatomical_region": None,
         "note": "BPD measurement — 49mm",
         "uploaded_by": str(user_id), "uploaded_at": s2_done - timedelta(minutes=20)},

        {"scan_id": str(s2_id), "patient_id": str(p2_id),
         "url": IMAGES["fetal_face"],
         "public_id": "radflow/frames/grace_face_001",
         "filename": "fetal_face_anatomy.jpg", "mime_type": "image/jpeg",
         "size_bytes": 102_400, "width": 400, "height": 400,
         "ai_suggested": False, "ai_event_type": None,
         "anatomical_region": None,
         "note": "Fetal face — anatomy survey",
         "uploaded_by": str(user_id), "uploaded_at": s2_done - timedelta(minutes=10)},

        # Emeka Nwosu — chest (2 captures)
        {"scan_id": str(s3_id), "patient_id": str(p3_id),
         "url": IMAGES["chest_tb"],
         "public_id": "radflow/frames/emeka_chest_001",
         "filename": "chest_rul_opacity.jpg", "mime_type": "image/jpeg",
         "size_bytes": 115_712, "width": 400, "height": 453,
         "ai_suggested": True, "ai_event_type": "possible_abnormality",
         "anatomical_region": None,
         "note": "RUL opacity — possible PTB",
         "uploaded_by": str(user_id), "uploaded_at": s3_done - timedelta(minutes=5)},

        {"scan_id": str(s3_id), "patient_id": str(p3_id),
         "url": IMAGES["chest_normal"],
         "public_id": "radflow/frames/emeka_chest_002",
         "filename": "chest_left_clear.jpg", "mime_type": "image/jpeg",
         "size_bytes": 89_088, "width": 400, "height": 449,
         "ai_suggested": False, "ai_event_type": None,
         "anatomical_region": None,
         "note": "Left lung — clear",
         "uploaded_by": str(user_id), "uploaded_at": s3_done - timedelta(minutes=3)},

        # Abdomen reference — useful if demo needs abdominal scan
        {"scan_id": str(s2_id), "patient_id": str(p2_id),
         "url": IMAGES["abdomen_gallstone"],
         "public_id": "radflow/frames/demo_gallstone_ref",
         "filename": "abdomen_gallstone_ref.jpg", "mime_type": "image/jpeg",
         "size_bytes": 76_800, "width": 400, "height": 326,
         "ai_suggested": False, "ai_event_type": None,
         "anatomical_region": None,
         "note": "Reference — gallstone appearance",
         "uploaded_by": str(user_id), "uploaded_at": s2_done - timedelta(minutes=25)},
    ])
    print("  + 8 media items (real images, anatomical_region tagged)")

    # ── Report templates ──────────────────────────────────────────────────────
    await db["templates"].insert_many([
        {
            "name": "Standard Breast Ultrasound",
            "scan_type": "breast_ultrasound",
            "structure": ["Clinical Indication", "Technique",
                          "Right Breast", "Left Breast", "Axillary Lymph Nodes",
                          "Impression", "BI-RADS", "Recommendation"],
            "default_technique":
                "Real-time grey-scale ultrasound of both breasts performed "
                "using a high-frequency linear probe.",
            "created_by": "global", "created_at": now,
        },
        {
            "name": "Standard Obstetric Ultrasound",
            "scan_type": "fetal_ultrasound",
            "structure": ["Clinical Indication", "Technique",
                          "Lie & Presentation", "Cardiac Activity",
                          "Biometry", "EFW", "Amniotic Fluid",
                          "Placenta", "Anatomy Survey", "Doppler", "Impression"],
            "default_technique":
                "Transabdominal ultrasound performed using a curvilinear probe.",
            "created_by": "global", "created_at": now,
        },
        {
            "name": "Standard Chest X-Ray",
            "scan_type": "chest_xray",
            "structure": ["Clinical Indication", "Technique",
                          "Lung Fields", "Cardiac Silhouette", "Mediastinum",
                          "Pleura", "Diaphragm", "Bones", "Impression"],
            "default_technique": "PA chest radiograph obtained in full inspiration.",
            "created_by": "global", "created_at": now,
        },
    ])
    print("  + 3 global report templates")

    # ── Checklist configs ─────────────────────────────────────────────────────
    for scan_type, items in CHECKLISTS.items():
        await db["checklist_configs"].insert_one({
            "_id": ObjectId(),
            "scan_type": scan_type,
            "items": items,
            "created_at": now,
        })
    print(f"  + {len(CHECKLISTS)} checklist configs")

    client.close()

    print("\n=== Seed complete! ===")
    print("  Login:    demo@radflow.com  /  radflow123")
    print("  Name:     Dr. Roberts  (hybrid)")
    print("")
    print("  Dashboard counters:")
    print("    Waiting:          3  (Amaka in-progress + Funke + Sarah pending)")
    print("    In Progress:      1  (Amaka Johnson)")
    print("    Completed Today:  2  (Grace Okafor + Emeka Nwosu)")
    print("")
    print("  Recently Completed table:")
    print("    Grace Okafor  — Fetal US  — HIGH risk  — Suspicious")
    print("    Emeka Nwosu   — Chest XR  — MODERATE   — Physician-provided")
    print("")
    print("  Images: real Wikipedia Commons ultrasound/x-ray photos")
    print("  API docs: http://localhost:8000/docs")


if __name__ == "__main__":
    asyncio.run(seed())
