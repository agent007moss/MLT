import pytest
from app.db.session import AsyncSessionLocal
from app.modules.settings.service import SettingsService


@pytest.mark.asyncio
async def test_settings_card_lifecycle():
    async with AsyncSessionLocal() as db:
        await SettingsService.seed_defaults(db)
        cards = await SettingsService.list_cards(db)
        assert len(cards) >= 14

        new = await SettingsService.create_card(db, 1, "new_card", "New Card", "desc")
        assert new.key == "new_card"

        updated = await SettingsService.update_card(db, 1, new.id, {"active": False})
        assert updated.active is False

        deleted = await SettingsService.delete_card(db, 1, new.id)
        assert deleted is True
