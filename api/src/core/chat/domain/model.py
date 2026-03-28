from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class Chat(BaseModel):
    id: UUID | None = None
    workspace_id: UUID
    name: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
