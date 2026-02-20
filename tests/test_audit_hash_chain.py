import pytest
from app.db.session import AsyncSessionLocal
from app.modules.audit.service import AuditService


@pytest.mark.asyncio
async def test_audit_chain_integrity():
    async with AsyncSessionLocal() as db:
        await AuditService.add_event(db, 1, "a", "t", {"x": 1})
        await AuditService.add_event(db, 1, "b", "t", {"x": 2})
        await db.commit()
        assert await AuditService.verify_chain(db)
