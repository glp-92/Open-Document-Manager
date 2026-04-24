from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel


class Owner(StrEnum):
    HUMAN = "HUMAN"
    AI = "AI"


class Message(BaseModel):
    id: UUID | None = None
    chat_id: UUID
    owner: Owner
    content: str
    created_at: datetime | None = None
    updated_at: datetime | None = None
