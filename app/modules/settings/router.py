from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.modules.auth.deps import get_current_user
from app.modules.rbac.deps import require_permission
from app.modules.settings.schemas import CardDefinitionCreate, CardDefinitionUpdate, SaveLayoutRequest
from app.modules.settings.service import SettingsService

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("/cards")
async def list_cards(db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    cards = await SettingsService.list_cards(db)
    return cards


@router.post("/cards", dependencies=[Depends(require_permission("settings:write"))])
async def create_card(payload: CardDefinitionCreate, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    return await SettingsService.create_card(db, current_user.id, payload.key, payload.title, payload.description)


@router.patch("/cards/{card_id}", dependencies=[Depends(require_permission("settings:write"))])
async def update_card(card_id: int, payload: CardDefinitionUpdate, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    card = await SettingsService.update_card(db, current_user.id, card_id, payload.model_dump())
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    return card


@router.delete("/cards/{card_id}", dependencies=[Depends(require_permission("settings:write"))])
async def delete_card(card_id: int, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    ok = await SettingsService.delete_card(db, current_user.id, card_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Card not found")
    return {"ok": True}


@router.get("/layout")
async def get_layout(db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    prefs = await SettingsService.get_user_layout(db, current_user.id)
    return prefs


@router.put("/layout")
async def save_layout(payload: SaveLayoutRequest, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    await SettingsService.save_user_layout(db, current_user.id, [x.model_dump() for x in payload.cards])
    return {"ok": True}
