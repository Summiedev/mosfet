"""
Media router — frame/clip upload and retrieval for scan sessions.

POST /media/upload   — accepts base64 OR multipart file upload
GET  /media          — list all media for a scan (?scanId=:id)
DELETE /media/:id    — remove a media item
"""
import base64
import io
import uuid
from datetime import datetime, timezone

from bson import ObjectId
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import JSONResponse

from app.core.database import media_col, scans_col
from app.core.security import get_current_user
from app.schemas.radflow import MediaOut, MediaUploadResponse
from app.services.media_service import upload_media, get_media_for_scan, delete_media
from app.core.config import settings

router = APIRouter(prefix="/media", tags=["Media"])

ALLOWED_MIME = {
    # Images (frame captures)
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/gif",
    # Video clips — short sequences showing motion or flow
    "video/mp4",
    "video/webm",
    "video/quicktime",   # .mov from iOS/macOS devices
}

# Cloudinary uses different upload resource type for video vs image
def _resource_type(mime: str) -> str:
    return "video" if mime.startswith("video/") else "image"
MAX_BYTES = settings.MEDIA_MAX_SIZE_MB * 1024 * 1024


def _serialize(doc: dict) -> MediaOut:
    return MediaOut(
        id=str(doc["_id"]),
        scan_id=doc["scan_id"],
        patient_id=doc["patient_id"],
        url=doc["url"],
        public_id=doc["public_id"],
        filename=doc["filename"],
        mime_type=doc["mime_type"],
        size_bytes=doc["size_bytes"],
        width=doc.get("width"),
        height=doc.get("height"),
        ai_suggested=doc.get("ai_suggested", False),
        ai_event_type=doc.get("ai_event_type"),
        anatomical_region=doc.get("anatomical_region"),
        note=doc.get("note"),
        uploaded_by=str(doc["uploaded_by"]),
        uploaded_at=doc["uploaded_at"],
    )


# ── POST /media/upload ────────────────────────────────────────────────────────
# Accepts EITHER:
#   a) multipart form: file + scan_id + patient_id [+ ai_suggested + note]
#   b) JSON body with base64_data + mime_type + filename + scan_id + patient_id

@router.post("/upload", response_model=MediaUploadResponse, status_code=201)
async def upload_frame(
    scan_id: str = Form(...),
    patient_id: str = Form(...),
    ai_suggested: bool = Form(False),
    ai_event_type: str = Form(None),
    anatomical_region: str = Form(None),
    note: str = Form(None),
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    # Validate scan exists
    try:
        scan = await scans_col().find_one({"_id": ObjectId(scan_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid scan_id")
    if not scan:
        raise HTTPException(status_code=404, detail="Scan session not found")

    # Validate mime type
    mime = file.content_type or "image/jpeg"
    if mime not in ALLOWED_MIME:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file type '{mime}'. Allowed: {', '.join(ALLOWED_MIME)}",
        )

    # Read bytes
    file_bytes = await file.read()
    if len(file_bytes) > MAX_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Max size: {settings.MEDIA_MAX_SIZE_MB} MB",
        )

    filename = file.filename or f"frame_{uuid.uuid4().hex[:8]}.jpg"

    doc = await upload_media(
        scan_id=scan_id,
        patient_id=patient_id,
        uploaded_by=current_user["id"],
        file_bytes=file_bytes,
        filename=filename,
        mime_type=mime,
        ai_suggested=ai_suggested,
        ai_event_type=ai_event_type,
        anatomical_region=anatomical_region,
        note=note,
    )

    return MediaUploadResponse(
        id=str(doc["_id"]),
        url=doc["url"],
        public_id=doc["public_id"],
        filename=doc["filename"],
        size_bytes=doc["size_bytes"],
        width=doc.get("width"),
        height=doc.get("height"),
        anatomical_region=doc.get("anatomical_region"),
        uploaded_at=doc["uploaded_at"],
    )


# ── POST /media/upload-base64 ─────────────────────────────────────────────────
# Alternative endpoint for when frontend captures canvas frames as base64

@router.post("/upload-base64", response_model=MediaUploadResponse, status_code=201)
async def upload_frame_base64(
    body: dict,
    current_user: dict = Depends(get_current_user),
):
    """
    Body: {
      "scan_id": str,
      "patient_id": str,
      "base64_data": "data:image/jpeg;base64,/9j/4AAQ...",
      "filename": "frame_001.jpg",       optional
      "ai_suggested": bool,              optional
      "ai_event_type": str,              optional
      "note": str                        optional
    }
    """
    scan_id = body.get("scan_id")
    patient_id = body.get("patient_id")
    b64_data = body.get("base64_data", "")

    if not scan_id or not patient_id or not b64_data:
        raise HTTPException(status_code=400, detail="scan_id, patient_id and base64_data are required")

    # Validate scan exists
    try:
        scan = await scans_col().find_one({"_id": ObjectId(scan_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid scan_id")
    if not scan:
        raise HTTPException(status_code=404, detail="Scan session not found")

    # Parse data URI
    if "," in b64_data:
        header, b64 = b64_data.split(",", 1)
        # Extract mime from "data:image/jpeg;base64"
        mime = header.replace("data:", "").replace(";base64", "")
    else:
        b64 = b64_data
        mime = "image/jpeg"

    if mime not in ALLOWED_MIME:
        raise HTTPException(status_code=415, detail=f"Unsupported type: {mime}")

    try:
        file_bytes = base64.b64decode(b64)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid base64 data")

    if len(file_bytes) > MAX_BYTES:
        raise HTTPException(status_code=413, detail=f"File too large. Max {settings.MEDIA_MAX_SIZE_MB} MB")

    filename = body.get("filename") or f"frame_{uuid.uuid4().hex[:8]}.jpg"

    doc = await upload_media(
        scan_id=scan_id,
        patient_id=patient_id,
        uploaded_by=current_user["id"],
        file_bytes=file_bytes,
        filename=filename,
        mime_type=mime,
        ai_suggested=body.get("ai_suggested", False),
        ai_event_type=body.get("ai_event_type"),
        anatomical_region=body.get("anatomical_region"),
        note=body.get("note"),
    )

    return MediaUploadResponse(
        id=str(doc["_id"]),
        url=doc["url"],
        public_id=doc["public_id"],
        filename=doc["filename"],
        size_bytes=doc["size_bytes"],
        width=doc.get("width"),
        height=doc.get("height"),
        anatomical_region=doc.get("anatomical_region"),
        uploaded_at=doc["uploaded_at"],
    )


# ── GET /media?scanId=:id ─────────────────────────────────────────────────────

@router.get("", response_model=list[MediaOut])
async def list_media(
    scanId: str = Query(..., description="Scan session ID"),
    current_user: dict = Depends(get_current_user),
):
    docs = await get_media_for_scan(scanId)
    return [_serialize(d) for d in docs]


# ── DELETE /media/:id ─────────────────────────────────────────────────────────

@router.delete("/{media_id}", status_code=204)
async def remove_media(
    media_id: str,
    current_user: dict = Depends(get_current_user),
):
    deleted = await delete_media(media_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Media item not found")
