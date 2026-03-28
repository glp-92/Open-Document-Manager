from typing import Literal

from pydantic import BaseModel


class DocumentFilters(BaseModel):
    limit: int | None = None
    offset: int | None = None
    order_by: Literal["filename", "created_at", "updated_at", "size"] = "updated_at"
    order: Literal["asc", "desc"] = "desc"
    filename: str | None = None


class NewDocumentRequest(BaseModel):
    filename: str


class UpdateDocumentRequest(BaseModel):
    filename: str
