from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ChatResponse(BaseModel):
    id: UUID
    name: str
    created_at: datetime
    updated_at: datetime


class ChatListResponse(BaseModel):
    total: int
    chats: list[ChatResponse]
