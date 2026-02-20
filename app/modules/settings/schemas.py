from pydantic import BaseModel, Field


class CardDefinitionCreate(BaseModel):
    key: str = Field(min_length=2, max_length=120)
    title: str = Field(min_length=2, max_length=200)
    description: str = Field(default="", max_length=400)


class CardDefinitionUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    active: bool | None = None


class UserCardPreference(BaseModel):
    card_key: str
    order_index: int
    visible: bool = True


class SaveLayoutRequest(BaseModel):
    cards: list[UserCardPreference]
