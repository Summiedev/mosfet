

CHECKLISTS: dict[str, list[dict]] = {
    "breast_ultrasound": [
        {"key": "clinical_indication",   "label": "Clinical indication documented",  "completed": False},
        {"key": "right_breast",          "label": "Right breast evaluated",           "completed": False},
        {"key": "left_breast",           "label": "Left breast evaluated",            "completed": False},
        {"key": "lesion_detected",       "label": "Lesion presence noted (yes/no)",   "completed": False},
        {"key": "lesion_location",       "label": "Lesion location specified",        "completed": False},
        {"key": "lesion_size",           "label": "Lesion size measured",             "completed": False},
        {"key": "lesion_margins",        "label": "Margins characterised",            "completed": False},
        {"key": "lesion_echogenicity",   "label": "Echogenicity described",           "completed": False},
        {"key": "posterior_features",    "label": "Posterior acoustic features noted","completed": False},
        {"key": "axillary_nodes",        "label": "Axillary lymph nodes evaluated",   "completed": False},
        {"key": "birads",                "label": "BI-RADS category assigned",        "completed": False},
    ],
    "fetal_ultrasound": [
        {"key": "clinical_indication",   "label": "Clinical indication documented",  "completed": False},
        {"key": "gestational_age",       "label": "Gestational age estimated",        "completed": False},
        {"key": "fetal_number",          "label": "Number of fetuses noted",          "completed": False},
        {"key": "fetal_presentation",    "label": "Fetal presentation documented",    "completed": False},
        {"key": "fetal_heartbeat",       "label": "Fetal cardiac activity confirmed", "completed": False},
        {"key": "biometry_bpd",          "label": "BPD measured",                    "completed": False},
        {"key": "biometry_hc",           "label": "Head circumference measured",      "completed": False},
        {"key": "biometry_ac",           "label": "Abdominal circumference measured", "completed": False},
        {"key": "biometry_fl",           "label": "Femur length measured",            "completed": False},
        {"key": "efw",                   "label": "Estimated fetal weight calculated","completed": False},
        {"key": "amniotic_fluid",        "label": "Amniotic fluid index assessed",    "completed": False},
        {"key": "placenta_location",     "label": "Placenta location documented",     "completed": False},
        {"key": "anatomy_survey",        "label": "Fetal anatomy survey completed",   "completed": False},
    ],
    "chest_xray": [
        {"key": "clinical_indication",   "label": "Clinical indication documented",  "completed": False},
        {"key": "projection",            "label": "Projection documented (PA/AP/Lat)","completed": False},
        {"key": "technical_quality",     "label": "Technical quality assessed",       "completed": False},
        {"key": "lung_fields",           "label": "Lung fields evaluated",            "completed": False},
        {"key": "cardiac_silhouette",    "label": "Cardiac silhouette assessed",      "completed": False},
        {"key": "mediastinum",           "label": "Mediastinum evaluated",            "completed": False},
        {"key": "pleura",                "label": "Pleural spaces checked",           "completed": False},
        {"key": "diaphragm",             "label": "Diaphragm contour documented",     "completed": False},
        {"key": "bones",                 "label": "Visible bony structures reviewed", "completed": False},
        {"key": "soft_tissues",          "label": "Soft tissues reviewed",            "completed": False},
    ],
    "abdominal_ultrasound": [
        {"key": "clinical_indication",   "label": "Clinical indication documented",  "completed": False},
        {"key": "liver",                 "label": "Liver evaluated",                  "completed": False},
        {"key": "gallbladder",           "label": "Gallbladder evaluated",            "completed": False},
        {"key": "bile_ducts",            "label": "Bile ducts assessed",              "completed": False},
        {"key": "pancreas",              "label": "Pancreas evaluated",               "completed": False},
        {"key": "spleen",                "label": "Spleen evaluated",                 "completed": False},
        {"key": "kidneys",               "label": "Both kidneys evaluated",           "completed": False},
        {"key": "aorta",                 "label": "Aorta assessed",                   "completed": False},
        {"key": "free_fluid",            "label": "Free fluid assessed",              "completed": False},
    ],
    "pelvic_ultrasound": [
        {"key": "clinical_indication",   "label": "Clinical indication documented",  "completed": False},
        {"key": "uterus_size",           "label": "Uterus size and morphology",       "completed": False},
        {"key": "endometrium",           "label": "Endometrial thickness measured",   "completed": False},
        {"key": "right_ovary",           "label": "Right ovary evaluated",            "completed": False},
        {"key": "left_ovary",            "label": "Left ovary evaluated",             "completed": False},
        {"key": "adnexa",                "label": "Adnexal regions assessed",         "completed": False},
        {"key": "free_fluid",            "label": "Free fluid assessed",              "completed": False},
        {"key": "bladder",               "label": "Urinary bladder assessed",         "completed": False},
    ],
}

# ── Required fields for validation ───────────────────────────────────────────
# These MUST be completed before a scan can be finalised

REQUIRED_KEYS: dict[str, list[str]] = {
    "breast_ultrasound":   ["clinical_indication", "right_breast", "left_breast",
                             "lesion_detected", "birads"],
    "fetal_ultrasound":    ["clinical_indication", "gestational_age", "fetal_heartbeat",
                             "biometry_bpd", "biometry_fl", "amniotic_fluid"],
    "chest_xray":          ["clinical_indication", "lung_fields", "cardiac_silhouette",
                             "mediastinum"],
    "abdominal_ultrasound":["clinical_indication", "liver", "kidneys"],
    "pelvic_ultrasound":   ["clinical_indication", "uterus_size", "right_ovary",
                             "left_ovary"],
}


def get_checklist(scan_type: str) -> list[dict]:
    return [item.copy() for item in CHECKLISTS.get(scan_type, [])]


def get_required_keys(scan_type: str) -> list[str]:
    return REQUIRED_KEYS.get(scan_type, [])
