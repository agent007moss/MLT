import hashlib
import json
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import AuditEvent


class AuditService:
    @staticmethod
    async def add_event(db: AsyncSession, actor_user_id: int | None, action: str, target: str, details: dict) -> AuditEvent:
        prev = await db.scalar(select(AuditEvent).order_by(desc(AuditEvent.id)).limit(1))
        prev_hash = prev.event_hash if prev else "GENESIS"
        payload = f"{actor_user_id}|{action}|{target}|{json.dumps(details, sort_keys=True)}|{prev_hash}"
        event_hash = hashlib.sha256(payload.encode()).hexdigest()
        event = AuditEvent(
            actor_user_id=actor_user_id,
            action=action,
            target=target,
            details=json.dumps(details),
            prev_hash=prev_hash,
            event_hash=event_hash,
        )
        db.add(event)
        await db.flush()
        return event

    @staticmethod
    async def verify_chain(db: AsyncSession) -> bool:
        events = (await db.execute(select(AuditEvent).order_by(AuditEvent.id))).scalars().all()
        prev_hash = "GENESIS"
        for event in events:
            payload = f"{event.actor_user_id}|{event.action}|{event.target}|{json.dumps(json.loads(event.details), sort_keys=True)}|{prev_hash}"
            expected_hash = hashlib.sha256(payload.encode()).hexdigest()
            if event.prev_hash != prev_hash or event.event_hash != expected_hash:
                return False
            prev_hash = event.event_hash
        return True
