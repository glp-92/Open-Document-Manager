from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class Document(BaseModel):
    id: UUID | None = None
    filename: str
    url: str | None = None
    size: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
