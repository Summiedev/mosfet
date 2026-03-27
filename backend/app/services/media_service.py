
import base64
import hashlib
import hmac
import io
import time
import uuid
from datetime import datetime, timezone

import httpx

from app.core.config import settings
from app.core.database import media_col


# ── Internal helpers ──────────────────────────────────────────────────────────

def _signed_params(public_id: str, folder: str, timestamp: int) -> dict:
    """Build Cloudinary signed upload params (for when you need signed uploads)."""
    params = {
        "folder": folder,
        "public_id": public_id,
        "timestamp": str(timestamp),
    }
    param_str = "&".join(f"{k}={v}" for k, v in sorted(params.items()))
    sig_input = param_str + settings.CLOUDINARY_API_SECRET
    signature = hashlib.sha256(sig_input.encode()).hexdigest()
    return {**params, "signature": signature, "api_key": settings.CLOUDINARY_API_KEY}


def _dev_placeholder(filename: str) -> dict:
    """Returns a fake upload result for development without Cloudinary."""
    fake_id = f"dev_{uuid.uuid4().hex[:8]}"
    return {
        "secure_url": f"https://placeholder.radflow.dev/frames/{fake_id}/{filename}",
        "public_id": fake_id,
        "bytes": 0,
        "width": 640,
        "height": 480,
        "format": "jpg",
    }


async def _upload_to_cloudinary(
    file_bytes: bytes,
    filename: str,
    mime_type: str,
    resource_type: str = "image",
) -> dict:
    """
    Upload raw bytes to Cloudinary.
    Returns Cloudinary response dict with secure_url, public_id, bytes, width, height.
    """
    cloud = settings.CLOUDINARY_CLOUD_NAME
    upload_url = f"https://api.cloudinary.com/v1_1/{cloud}/{resource_type}/upload"

    timestamp = int(time.time())
    public_id = f"{uuid.uuid4().hex[:12]}_{filename.rsplit('.', 1)[0]}"
    folder = settings.CLOUDINARY_FOLDER

    # Use signed upload (more secure than unsigned presets)
    params = _signed_params(public_id, folder, timestamp)

    # Encode file as base64 data URI for upload
    b64 = base64.b64encode(file_bytes).decode()
    data_uri = f"data:{mime_type};base64,{b64}"

    form_data = {**params, "file": data_uri}

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(upload_url, data=form_data)
        resp.raise_for_status()
        return resp.json()


# ── Public API ────────────────────────────────────────────────────────────────

async def upload_media(
    scan_id: str,
    patient_id: str,
    uploaded_by: str,
    file_bytes: bytes,
    filename: str,
    mime_type: str,
    ai_suggested: bool = False,
    ai_event_type: str | None = None,
    anatomical_region: str | None = None,
    note: str | None = None,
) -> dict:
    """
    Upload a frame to Cloudinary (or dev placeholder), persist metadata to MongoDB.
    Returns the saved media document dict.
    """
    resource_type = "video" if mime_type.startswith("video/") else "image"

    if not settings.CLOUDINARY_CLOUD_NAME or settings.APP_ENV == "development":
        print(f"[MEDIA DEV] Skipping Cloudinary upload for {filename} ({resource_type})")
        upload_result = _dev_placeholder(filename)
    else:
        upload_result = await _upload_to_cloudinary(file_bytes, filename, mime_type, resource_type)

    now = datetime.now(timezone.utc)
    doc = {
        "scan_id": scan_id,
        "patient_id": patient_id,
        "url": upload_result["secure_url"],
        "public_id": upload_result["public_id"],
        "filename": filename,
        "mime_type": mime_type,
        "size_bytes": upload_result.get("bytes", len(file_bytes)),
        "width": upload_result.get("width"),
        "height": upload_result.get("height"),
        "ai_suggested": ai_suggested,
        "ai_event_type": ai_event_type,
        "anatomical_region": anatomical_region,
        "note": note,
        "uploaded_by": uploaded_by,
        "uploaded_at": now,
    }

    result = await media_col().insert_one(doc)
    doc["_id"] = result.inserted_id
    return doc


async def get_media_for_scan(scan_id: str) -> list[dict]:
    """Return all media items for a scan, sorted oldest-first."""
    cursor = media_col().find({"scan_id": scan_id}).sort("uploaded_at", 1)
    return await cursor.to_list(length=200)


async def delete_media(media_id: str) -> bool:
    """Delete a media item from DB (Cloudinary deletion requires signed destroy call)."""
    from bson import ObjectId
    result = await media_col().delete_one({"_id": ObjectId(media_id)})
    return result.deleted_count > 0
