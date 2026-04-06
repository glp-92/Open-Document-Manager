from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel


class Status(StrEnum):
    PENDING = "pending"
    COMPLETED = "completed"
    ERROR = "error"
    DELETED = "deleted"


class Run(BaseModel):
    id: UUID | None = None
    workspace_id: UUID
    status: Status = Status.PENDING
    created_at: datetime | None = None
    completed_at: datetime | None = None
    updated_at: datetime | None = None
