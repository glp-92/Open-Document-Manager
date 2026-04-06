from uuid import UUID

from core.run.api.dto.requests import (
    NewRunRequest,
    RunFilters,
)
from core.run.api.dto.responses import (
    RunListResponse,
    RunResponse,
)
from core.run.domain.model import Run
from core.run.exceptions.run import RunNotFoundError
from core.run.infrastructure.db_model import DBRun
from core.run.infrastructure.repository_impl import RunRepositoryImpl
from sqlalchemy.ext.asyncio import AsyncSession


class RunService:
    def __init__(self, run_repository_impl: RunRepositoryImpl):
        self.run_repository_impl = run_repository_impl

    async def create_run(self, session: AsyncSession, new_run_request: NewRunRequest) -> RunResponse:
        run: Run = Run(**new_run_request.model_dump())
        db_run = await self.run_repository_impl.save(session=session, run=run)
        return RunResponse(
            id=db_run.id,
            workspace_id=db_run.workspace_id,
            status=db_run.status,
            created_at=db_run.created_at,
            updated_at=db_run.updated_at,
            completed_at=db_run.completed_at,
        )

    async def find_runs_with_filters_pageable(self, session: AsyncSession, filters: RunFilters) -> RunListResponse:
        db_runs: list[DBRun] = []
        total: int = 0
        db_runs, total = await self.run_repository_impl.find_many_filtered_pageable(session=session, filters=filters)
        return RunListResponse(
            runs=[RunResponse.model_validate(obj=db_run, from_attributes=True) for db_run in db_runs],
            total=total,
        )

    async def delete_run_by_id(self, session: AsyncSession, run_id: UUID):
        deleted_id: UUID | None = await self.run_repository_impl.delete_by_id(session=session, id=run_id)
        if deleted_id is None:
            raise RunNotFoundError(run_id=run_id)
        return
