"""
Templates router.

GET  /templates              — list all templates for current user (+ global ones)
POST /templates              — create a new template
GET  /templates/:id          — get single template
DELETE /templates/:id        — delete a template (owner only)
"""
from datetime import datetime, timezone

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.database import templates_col
from app.core.security import get_current_user
from app.schemas.radflow import TemplateCreate, TemplateOut

router = APIRouter(prefix="/templates", tags=["Templates"])


def _serialize(doc: dict) -> TemplateOut:
    return TemplateOut(
        id=str(doc["_id"]),
        name=doc["name"],
        scan_type=doc["scan_type"],
        structure=doc["structure"],
        default_technique=doc.get("default_technique"),
        created_by=str(doc["created_by"]),
        created_at=doc["created_at"],
    )


# ── GET /templates ────────────────────────────────────────────────────────────

@router.get("", response_model=list[TemplateOut])
async def list_templates(
    scan_type: str = Query(None, description="Filter by scan type"),
    current_user: dict = Depends(get_current_user),
):
    """
    Returns templates owned by the current user PLUS any global templates
    (global = created_by == "global").
    """
    user_oid = ObjectId(current_user["id"])
    query: dict = {
        "$or": [
            {"created_by": user_oid},
            {"created_by": "global"},
        ]
    }
    if scan_type:
        query["scan_type"] = scan_type

    cursor = templates_col().find(query).sort("created_at", -1)
    docs = await cursor.to_list(length=100)
    return [_serialize(d) for d in docs]


# ── POST /templates ───────────────────────────────────────────────────────────

@router.post("", response_model=TemplateOut, status_code=201)
async def create_template(
    body: TemplateCreate,
    current_user: dict = Depends(get_current_user),
):
    # Prevent duplicate name per user + scan_type
    exists = await templates_col().find_one({
        "name": body.name,
        "scan_type": body.scan_type,
        "created_by": ObjectId(current_user["id"]),
    })
    if exists:
        raise HTTPException(
            status_code=409,
            detail=f"You already have a template named '{body.name}' for {body.scan_type}",
        )

    now = datetime.now(timezone.utc)
    doc = {
        "name": body.name,
        "scan_type": body.scan_type,
        "structure": body.structure,
        "default_technique": body.default_technique,
        "created_by": ObjectId(current_user["id"]),
        "created_at": now,
        "updated_at": now,
    }
    result = await templates_col().insert_one(doc)
    doc["_id"] = result.inserted_id
    return _serialize(doc)


# ── GET /templates/:id ────────────────────────────────────────────────────────

@router.get("/{template_id}", response_model=TemplateOut)
async def get_template(
    template_id: str,
    current_user: dict = Depends(get_current_user),
):
    try:
        oid = ObjectId(template_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid template ID")

    doc = await templates_col().find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=404, detail="Template not found")
    return _serialize(doc)


# ── DELETE /templates/:id ─────────────────────────────────────────────────────

@router.delete("/{template_id}", status_code=204)
async def delete_template(
    template_id: str,
    current_user: dict = Depends(get_current_user),
):
    try:
        oid = ObjectId(template_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid template ID")

    doc = await templates_col().find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=404, detail="Template not found")

    # Only owner can delete
    if str(doc["created_by"]) != current_user["id"]:
        raise HTTPException(status_code=403, detail="You can only delete your own templates")

    await templates_col().delete_one({"_id": oid})
