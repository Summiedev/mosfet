from fastapi import APIRouter, HTTPException
from datetime import datetime
from bson import ObjectId

from database import db, fix_id
from models import ScanSessionCreate, UpdateTranscript, ChecklistItem

router = APIRouter(prefix="/scans", tags=["3. Scan Mode (Day 2)"])


@router.post("/start")
async def start_scan(session: ScanSessionCreate):
    # Setup standard checklist per scan type
    default_checklist = [
        {"item": "Patient positioning verified", "checked": False},
        {"item": "Artifact-free capture", "checked": False},
        {"item": "Region of Interest (ROI) centered", "checked": False}
    ]
    
    scan_dict = {
        "patient_id": session.patient_id,
        "scan_type": session.scan_type,
        "status": "In-Progress",
        "transcript": "   " ,
        "checklist": default_checklist,
        "images": [], # SAVES IMAGE
        "created_at": datetime.utcnow()
    }
    
    result = await db.scans.insert_one(scan_dict)
    return {"status": "Scan session live", "scan_id": str(result.inserted_id)}


@router.patch("/{scan_id}/transcript")
async def update_transcript(scan_id: str, data: UpdateTranscript):
    # SPEECH TO TEXT SAVES HERE
    await db.scans.update_one(
        {"_id": ObjectId(scan_id)},
        {"set": {"transcript": data.text}}
    )
    return {"status": "✅ Live Transcript saved!"}


@router.patch("/{scan_id}/checklist")
async def update_checklist(scan_id: str, data: ChecklistItem):
    #  WORK REQUIRED: Find the item in the list array and update its boolean
    await db.scans.update_one(
        {"_id": ObjectId(scan_id), "checklist.item": data.item_name},
        {"set": {"checklist checked": data.is_checked}}
    )
    return {"status": f" Checklist item '{data.item_name}' updated"}


@router.post("/{scan_id}/capture")
async def capture_frame(scan_id: str, frame_url: str):
    # WORK REQUIRED: Save captured image links to array
    await db.scans.update_one(
        {"_id": ObjectId(scan_id)},
        {"push": {"images": {"url": frame_url, "captured_at": datetime.utcnow()}}}
    )
    return {"status": " Image captured successfully!"}