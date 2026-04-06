from datetime import datetime
from uuid import UUID

from core.run.domain.model import Status
from pydantic import BaseModel


class RunResponse(BaseModel):
    id: UUID
    workspace_id: UUID
    status: Status
    created_at: datetime
    updated_at: datetime | None = None
    completed_at: datetime | None = None


class RunListResponse(BaseModel):
    total: int
    runs: list[RunResponse]
