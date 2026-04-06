from datetime import datetime
from typing import Literal
from uuid import UUID

from core.run.domain.model import Status
from pydantic import BaseModel


class RunFilters(BaseModel):
    limit: int | None = None
    offset: int | None = None
    order_by: Literal["workspace_id", "created_at", "updated_at", "completed_at", "status"] = "created_at"
    order: Literal["asc", "desc"] = "desc"
    workspace_id: UUID | None = None
    status: Status | None = None
    from_creation_date: datetime | None = None
    to_creation_date: datetime | None = None
    from_update_date: datetime | None = None
    to_update_date: datetime | None = None
    from_completion_date: datetime | None = None
    to_completion_date: datetime | None = None


class NewRunRequest(BaseModel):
    workspace_id: UUID
