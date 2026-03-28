from typing import Literal
from uuid import UUID

from pydantic import BaseModel


class DocumentFilters(BaseModel):
    limit: int | None = None
    offset: int | None = None
    order_by: Literal["filename", "chat_id", "created_at", "updated_at", "size"] = "updated_at"
    order: Literal["asc", "desc"] = "desc"
    filename: str | None = None
    chat_id: UUID | None = None


class NewDocumentRequest(BaseModel):
    chat_id: UUID
    filename: str
