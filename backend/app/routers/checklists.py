from fastapi import APIRouter, HTTPException, Depends

from app.core.security import get_current_user
from app.services.checklist_service import get_checklist, CHECKLISTS

router = APIRouter(prefix="/checklists", tags=["Checklists"])


@router.get("/{scan_type}")
async def get_checklist_for_scan(
    scan_type: str,
    current_user: dict = Depends(get_current_user),
):
    if scan_type not in CHECKLISTS:
        raise HTTPException(
            status_code=404,
            detail=f"No checklist defined for scan type '{scan_type}'. "
                   f"Valid types: {list(CHECKLISTS.keys())}",
        )
    return {
        "scan_type": scan_type,
        "items": get_checklist(scan_type),
        "total": len(get_checklist(scan_type)),
    }


@router.get("")
async def list_scan_types(current_user: dict = Depends(get_current_user)):
    return {"scan_types": list(CHECKLISTS.keys())}
