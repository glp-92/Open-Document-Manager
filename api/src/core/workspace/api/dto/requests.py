from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class WorkspaceFilters(BaseModel):
    limit: int | None = None
    offset: int | None = None
    order_by: Literal["name", "created_at", "updated_at"] = "updated_at"
    order: Literal["asc", "desc"] = "desc"
    name: str | None = None
    from_creation_date: datetime | None = None
    to_creation_date: datetime | None = None
    from_update_date: datetime | None = None
    to_update_date: datetime | None = None


class NewWorkspaceRequest(BaseModel):
    name: str


class UpdateWorkspaceRequest(BaseModel):
    name: str
