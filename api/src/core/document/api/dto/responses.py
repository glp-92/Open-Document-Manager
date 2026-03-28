from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class DocumentResponse(BaseModel):
    id: UUID
    chat_id: UUID
    filename: str
    url: str | None = None
    size: int | None = None
    created_at: datetime
    updated_at: datetime


class DocumentListResponse(BaseModel):
    total: int
    documents: list[DocumentResponse]
