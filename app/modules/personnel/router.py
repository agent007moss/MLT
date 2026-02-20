from fastapi import APIRouter, Depends
from app.modules.rbac.deps import require_permission

router = APIRouter(prefix="/personnel", tags=["personnel"])


@router.get("", dependencies=[Depends(require_permission("personnel:read"))])
async def list_personnel():
    return {"items": [], "message": "Personnel module scaffold"}


@router.post("", dependencies=[Depends(require_permission("personnel:write"))])
async def create_personnel():
    return {"ok": True, "message": "Create personnel scaffold"}
