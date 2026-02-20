from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import DashboardCardDefinition, UserDashboardPreference
from app.modules.audit.service import AuditService

DEFAULT_CARDS = [
    "Personal Data", "Contact Information", "Civilian Education", "Awards", "Fitness", "Appointments",
    "Counseling’s/NCOER/OER", "Duty Roster", "Per Stats", "HR Metrix", "Equipment", "Profiles",
    "Military Training", "Military Data",
]


class SettingsService:
    @staticmethod
    async def seed_defaults(db: AsyncSession) -> None:
        count = len((await db.execute(select(DashboardCardDefinition.id))).scalars().all())
        if count:
            return
        for title in DEFAULT_CARDS:
            key = title.lower().replace(" ", "_").replace("/", "_").replace("’", "")
            db.add(DashboardCardDefinition(key=key, title=title, description=f"{title} module"))
        await db.commit()

    @staticmethod
    async def list_cards(db: AsyncSession):
        return (await db.execute(select(DashboardCardDefinition).order_by(DashboardCardDefinition.id))).scalars().all()

    @staticmethod
    async def create_card(db: AsyncSession, actor_id: int, key: str, title: str, description: str):
        card = DashboardCardDefinition(key=key, title=title, description=description, active=True)
        db.add(card)
        await AuditService.add_event(db, actor_id, "settings.card.create", "dashboard_card", {"key": key})
        await db.commit()
        await db.refresh(card)
        return card

    @staticmethod
    async def update_card(db: AsyncSession, actor_id: int, card_id: int, data: dict):
        card = await db.get(DashboardCardDefinition, card_id)
        if not card:
            return None
        for k, v in data.items():
            if v is not None:
                setattr(card, k, v)
        await AuditService.add_event(db, actor_id, "settings.card.update", "dashboard_card", {"card_id": card_id})
        await db.commit()
        await db.refresh(card)
        return card

    @staticmethod
    async def delete_card(db: AsyncSession, actor_id: int, card_id: int):
        card = await db.get(DashboardCardDefinition, card_id)
        if not card:
            return False
        await db.delete(card)
        await AuditService.add_event(db, actor_id, "settings.card.delete", "dashboard_card", {"card_id": card_id})
        await db.commit()
        return True

    @staticmethod
    async def get_user_layout(db: AsyncSession, user_id: int):
        return (await db.execute(select(UserDashboardPreference).where(UserDashboardPreference.user_id == user_id).order_by(UserDashboardPreference.order_index))).scalars().all()

    @staticmethod
    async def save_user_layout(db: AsyncSession, user_id: int, cards: list[dict]):
        await db.execute(delete(UserDashboardPreference).where(UserDashboardPreference.user_id == user_id))
        for c in cards:
            db.add(UserDashboardPreference(user_id=user_id, card_key=c["card_key"], order_index=c["order_index"], visible=c["visible"]))
        await AuditService.add_event(db, user_id, "settings.layout.update", "dashboard_layout", {"cards": len(cards)})
        await db.commit()
