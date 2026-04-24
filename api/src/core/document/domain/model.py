from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel


class StorageStatus(StrEnum):
    PENDING = "PENDING"
    READY = "READY"
    ERROR = "ERROR"
    DELETED = "DELETED"


class Document(BaseModel):
    id: UUID | None = None
    workspace_id: UUID
    filename: str
    storage_status: StorageStatus = StorageStatus.PENDING
    url: str | None = None
    size: int | None = None
    mime: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
