from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel


class DocumentFilters(BaseModel):
    limit: int | None = None
    offset: int | None = None
    order_by: Literal["filename", "chat_id", "created_at", "updated_at", "size", "mime"] = "updated_at"
    order: Literal["asc", "desc"] = "desc"
    filename: str | None = None
    mime: str | None = None
    chat_id: UUID | None = None
    from_creation_date: datetime | None = None
    to_creation_date: datetime | None = None
    from_update_date: datetime | None = None
    to_update_date: datetime | None = None


class NewDocumentRequest(BaseModel):
    chat_id: UUID
    filename: str


class DocumentStorageWebhookEntryAttributes(BaseModel):
    file_size: int | None = None
    mime: str | None = None


class DocumentStorageWebhookEntry(BaseModel):
    name: str
    attributes: DocumentStorageWebhookEntryAttributes
    is_directory: bool | None = None


class DocumentStorageWebhookMessage(BaseModel):
    old_entry: DocumentStorageWebhookEntry | None = None
    new_entry: DocumentStorageWebhookEntry | None = None


class DocumentStorageWebhookRequest(BaseModel):
    event_type: Literal["create", "update", "rename", "delete"]
    key: str
    message: DocumentStorageWebhookMessage
