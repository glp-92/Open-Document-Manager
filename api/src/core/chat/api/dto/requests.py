from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel


class ChatFilters(BaseModel):
    limit: int | None = None
    offset: int | None = None
    order_by: Literal["name", "workspace_id", "created_at", "updated_at"] = "updated_at"
    order: Literal["asc", "desc"] = "desc"
    name: str | None = None
    workspace_id: UUID | None = None
    from_creation_date: datetime | None = None
    to_creation_date: datetime | None = None
    from_update_date: datetime | None = None
    to_update_date: datetime | None = None


class NewChatRequest(BaseModel):
    workspace_id: UUID
    name: str | None = None


class UpdateChatRequest(BaseModel):
    name: str
