from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel


class MessageResponse(BaseModel):
    id: UUID
    chat_id: UUID
    owner: Literal["human", "ai"]
    content: str
    created_at: datetime
    updated_at: datetime


class MessageListResponse(BaseModel):
    total: int
    messages: list[MessageResponse]
