from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class Workspace(BaseModel):
    id: UUID | None = None
    name: str
    created_at: datetime | None = None
    updated_at: datetime | None = None
