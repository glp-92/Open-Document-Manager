from datetime import datetime
from typing import Literal
from uuid import UUID

from core.document.domain.model import StorageStatus
from pydantic import BaseModel


class DocumentResponse(BaseModel):
    id: UUID
    workspace_id: UUID
    filename: str
    url: str | None = None
    size: int | None = None
    mime: str | None = None
    created_at: datetime
    updated_at: datetime
    storage_status: StorageStatus


class UploadDocumentOptimisticResponse(BaseModel):
    id: UUID
    workspace_id: UUID
    filename: str
    presigned_url: str
    created_at: datetime


class DocumentStorageWebhookResponse(BaseModel):
    status: Literal["ok", "error"] = "ok"


class DocumentListResponse(BaseModel):
    total: int
    documents: list[DocumentResponse]
