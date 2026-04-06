from uuid import UUID

from core.run.api.dto.requests import RunFilters
from core.run.domain.model import Run
from core.run.domain.repository import RunRepository
from core.run.infrastructure.db_model import DBRun
from core.shared.infrastructure.timestamps import normalize_timestamps_to_utc
from sqlalchemy import Column, Result, Select, delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession


class RunRepositoryImpl(RunRepository):
    def __init__(self):
        return

    @staticmethod
    async def save(session: AsyncSession, run: Run) -> DBRun:
        db_run: DBRun = DBRun.from_domain_object(run=run)
        session.add(db_run)
        await session.flush()
        return db_run

    @staticmethod
    async def find_many_filtered_pageable(session: AsyncSession, filters: RunFilters) -> tuple[list[DBRun], int]:
        def _apply_filters(stmt: Select):
            if filters.workspace_id:
                stmt = stmt.where(DBRun.workspace_id == filters.workspace_id)
            if filters.status:
                stmt = stmt.where(DBRun.status == filters.status)
            if filters.from_creation_date:
                stmt = stmt.where(DBRun.created_at >= normalize_timestamps_to_utc(filters.from_creation_date))
            if filters.to_creation_date:
                stmt = stmt.where(DBRun.created_at <= normalize_timestamps_to_utc(filters.to_creation_date))
            if filters.from_update_date:
                stmt = stmt.where(DBRun.created_at >= normalize_timestamps_to_utc(filters.from_update_date))
            if filters.to_update_date:
                stmt = stmt.where(DBRun.created_at <= normalize_timestamps_to_utc(filters.to_update_date))
            if filters.from_completion_date:
                stmt = stmt.where(DBRun.created_at >= normalize_timestamps_to_utc(filters.from_completion_date))
            if filters.to_completion_date:
                stmt = stmt.where(DBRun.created_at <= normalize_timestamps_to_utc(filters.to_completion_date))
            return stmt

        total_stmt = select(func.count()).select_from(DBRun)
        total_stmt = _apply_filters(stmt=total_stmt)
        total: int = (await session.execute(total_stmt)).scalar_one()
        stmt = select(DBRun)
        stmt = _apply_filters(stmt=stmt)
        column: Column = getattr(DBRun, filters.order_by)
        stmt = stmt.order_by(column.desc() if filters.order == "desc" else column.asc())
        if filters.limit is not None:
            stmt = stmt.limit(filters.limit)
        if filters.offset is not None:
            stmt = stmt.offset(filters.offset)
        result = await session.execute(stmt)
        db_runs: list[DBRun] = result.scalars().all()
        return db_runs, total

    @staticmethod
    async def find_by_id(session: AsyncSession, id: UUID) -> DBRun:
        stmt = select(DBRun).where(DBRun.id == id)
        db_run: DBRun = (await session.execute(stmt)).scalar_one_or_none()
        return db_run

    @staticmethod
    async def delete_by_id(session: AsyncSession, id: UUID) -> UUID | None:
        stmt = delete(DBRun).where(DBRun.id == id).returning(DBRun.id)
        result: Result = await session.execute(stmt)
        return result.scalar_one_or_none()
