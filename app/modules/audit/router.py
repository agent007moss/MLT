from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import AuditEvent
from app.db.session import get_db
from app.modules.audit.service import AuditService
from app.modules.rbac.deps import require_permission

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("/events", dependencies=[Depends(require_permission("audit:read"))])
async def list_audit_events(db: AsyncSession = Depends(get_db)):
    events = (await db.execute(select(AuditEvent).order_by(AuditEvent.id.desc()).limit(200))).scalars().all()
    return [
        {
            "id": e.id,
            "action": e.action,
            "target": e.target,
            "details": e.details,
            "created_at": e.created_at,
            "event_hash": e.event_hash,
            "prev_hash": e.prev_hash,
        }
        for e in events
    ]


@router.get("/verify-chain", dependencies=[Depends(require_permission("audit:read"))])
async def verify_chain(db: AsyncSession = Depends(get_db)):
    return {"valid": await AuditService.verify_chain(db)}
