from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel


class MessageFilters(BaseModel):
    limit: int | None = None
    offset: int | None = None
    order_by: Literal["owner", "chat_id", "created_at", "updated_at"] = "updated_at"
    order: Literal["asc", "desc"] = "desc"
    owner: Literal["HUMAN", "AI"] | None = None
    content: str | None = None
    chat_id: UUID | None = None
    from_creation_date: datetime | None = None
    to_creation_date: datetime | None = None
    from_update_date: datetime | None = None
    to_update_date: datetime | None = None


class NewMessageRequest(BaseModel):
    chat_id: UUID
    owner: Literal["HUMAN", "AI"] = "HUMAN"
    content: str
