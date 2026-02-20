from fastapi import APIRouter, Depends
from app.modules.rbac.deps import require_permission

router = APIRouter(prefix="/org", tags=["org"])


@router.get("", dependencies=[Depends(require_permission("org:read"))])
async def list_org_units():
    return {"items": [], "message": "Org module scaffold"}


@router.post("", dependencies=[Depends(require_permission("org:write"))])
async def create_org_unit():
    return {"ok": True, "message": "Create org scaffold"}
