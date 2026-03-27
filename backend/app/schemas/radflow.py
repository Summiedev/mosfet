from pydantic import BaseModel, Field
from typing import Any, Literal, Optional
from datetime import datetime


# ── Scan type / checklist ─────────────────────────────────────────────────────

ScanType = Literal[
    "breast_ultrasound",
    "fetal_ultrasound",
    "chest_xray",
    "abdominal_ultrasound",
    "pelvic_ultrasound",
]


# ── Patient ───────────────────────────────────────────────────────────────────

class PatientCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=120)
    age: Optional[int] = None
    sex: Optional[Literal["male", "female", "other"]] = None
    phone: Optional[str] = None


class PatientOut(BaseModel):
    id: str
    name: str
    age: Optional[int]
    sex: Optional[str]
    phone: Optional[str]
    created_by: str
    created_at: datetime


# ── Scan session ─────────────────────────────────────────────────────────────

class ScanCreate(BaseModel):
    patient_id: str
    scan_type: ScanType
    clinical_indication: str = Field(..., min_length=3, max_length=500)


class ChecklistItem(BaseModel):
    key: str
    label: str
    completed: bool = False
    value: Optional[str] = None


class AIEvent(BaseModel):
    timestamp_seconds: float
    event_type: Literal["possible_abnormality", "good_frame", "consider_capture", "info"]
    message: str
    frame_url: Optional[str] = None
    acknowledged: bool = False


class CapturedFrame(BaseModel):
    url: str
    captured_at: datetime
    ai_suggested: bool = False
    note: Optional[str] = None


class ScanUpdate(BaseModel):
    checklist: Optional[list[ChecklistItem]] = None
    transcript: Optional[str] = None
    captured_frames: Optional[list[CapturedFrame]] = None
    ai_flags: Optional[list[AIEvent]] = None


class ScanOut(BaseModel):
    id: str
    patient_id: str
    patient_name: str
    scan_type: str
    clinical_indication: str
    status: str                   # pending | in_progress | completed | validated
    checklist: list[ChecklistItem]
    transcript: str
    captured_frames: list[CapturedFrame]
    ai_flags: list[AIEvent]
    created_by: str
    created_at: datetime
    completed_at: Optional[datetime]


class ValidationResult(BaseModel):
    valid: bool
    missing_fields: list[str]
    warnings: list[str]


# ── Dashboard ─────────────────────────────────────────────────────────────────

class DashboardResponse(BaseModel):
    pending_scans: list[ScanOut]        # in_progress + pending, sorted: critical-flagged first
    recent_completed: list[ScanOut]     # within 48 h, sorted: high/critical risk first
    critical_cases: list[ScanOut]       # scans whose report has high or critical risk
    total_today: int


# ── Report ────────────────────────────────────────────────────────────────────

class ReportOut(BaseModel):
    id: str
    scan_id: str
    patient_id: str
    patient_name: str
    scan_type: str
    clinical_indication: str
    findings: str
    impression: str
    risk_level: Optional[Literal["low", "moderate", "high", "critical"]]
    template_id: Optional[str]
    is_final: bool
    created_by: str
    created_at: datetime
    finalised_at: Optional[datetime]


class ReportUpdate(BaseModel):
    findings: Optional[str] = None
    impression: Optional[str] = None


class RiskUpdate(BaseModel):
    risk_level: Literal["low", "moderate", "high", "critical"]


# ── AI events ─────────────────────────────────────────────────────────────────

class AIEventsResponse(BaseModel):
    scan_id: str
    events: list[AIEvent]


# ── Media ─────────────────────────────────────────────────────────────────────

class MediaOut(BaseModel):
    id: str
    scan_id: str
    patient_id: str
    url: str
    public_id: str               # Cloudinary public_id for deletion
    filename: str
    mime_type: str
    size_bytes: int
    width: Optional[int]
    height: Optional[int]
    ai_suggested: bool
    ai_event_type: Optional[str]
    anatomical_region: Optional[str]   # e.g. "UOQ", "UIQ", "LOQ", "LIQ", "AXL"
    note: Optional[str]
    uploaded_by: str
    uploaded_at: datetime


class MediaUploadResponse(BaseModel):
    id: str
    url: str
    public_id: str
    filename: str
    size_bytes: int
    width: Optional[int]
    height: Optional[int]
    anatomical_region: Optional[str]
    uploaded_at: datetime


# ── Templates ─────────────────────────────────────────────────────────────────

class TemplateCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    scan_type: ScanType
    structure: list[str] = Field(..., min_length=1,
        description="Ordered list of section headings, e.g. ['Clinical Indication', 'Findings', 'Impression']")
    default_technique: Optional[str] = None


class TemplateOut(BaseModel):
    id: str
    name: str
    scan_type: str
    structure: list[str]
    default_technique: Optional[str]
    created_by: str
    created_at: datetime


# ── Report generation ─────────────────────────────────────────────────────────

class ReportGenerateResponse(BaseModel):
    id: str
    scan_id: str
    patient_id: str
    patient_name: str
    scan_type: str
    clinical_indication: str
    technique: str
    findings: str
    impression: str
    risk_level: Optional[Literal["low", "moderate", "high", "critical"]]
    template_id: Optional[str]
    captured_frame_urls: list[str]
    is_final: bool
    created_by: str
    created_at: datetime
    finalised_at: Optional[datetime]


# ── E2E test result ───────────────────────────────────────────────────────────

class E2EStepResult(BaseModel):
    step: str
    status: Literal["pass", "fail", "skip"]
    detail: str


class E2ETestResponse(BaseModel):
    overall: Literal["pass", "fail"]
    steps: list[E2EStepResult]
    duration_ms: float
