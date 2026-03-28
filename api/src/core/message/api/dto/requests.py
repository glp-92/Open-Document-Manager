from typing import Literal
from uuid import UUID

from pydantic import BaseModel


class MessageFilters(BaseModel):
    limit: int | None = None
    offset: int | None = None
    order_by: Literal["owner", "created_at", "updated_at"] = "updated_at"
    order: Literal["asc", "desc"] = "desc"
    owner: Literal["human", "ai"] | None = None
    content: str | None = None


class NewMessageRequest(BaseModel):
    chat_id: UUID
    owner: Literal["human", "ai"] = "human"
    content: str
