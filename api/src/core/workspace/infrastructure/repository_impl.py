from uuid import UUID

from core.shared.infrastructure.timestamps import normalize_timestamps_to_utc
from core.workspace.api.dto.requests import UpdateWorkspaceRequest, WorkspaceFilters
from core.workspace.domain.model import Workspace
from core.workspace.domain.repository import WorkspaceRepository
from core.workspace.infrastructure.db_model import DBWorkspace
from sqlalchemy import Column, Result, Select, delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession


class WorkspaceRepositoryImpl(WorkspaceRepository):
    def __init__(self):
        return

    @staticmethod
    async def save(session: AsyncSession, workspace: Workspace) -> DBWorkspace:
        db_workspace: DBWorkspace = DBWorkspace.from_domain_object(workspace=workspace)
        session.add(db_workspace)
        await session.flush()
        return db_workspace

    @staticmethod
    async def find_many_filtered_pageable(
        session: AsyncSession, filters: WorkspaceFilters
    ) -> tuple[list[DBWorkspace], int]:
        def _apply_filters(stmt: Select):
            if filters.name:
                stmt = stmt.where(DBWorkspace.name.contains(filters.name))
            if filters.from_creation_date:
                stmt = stmt.where(DBWorkspace.created_at >= normalize_timestamps_to_utc(filters.from_creation_date))
            if filters.to_creation_date:
                stmt = stmt.where(DBWorkspace.created_at <= normalize_timestamps_to_utc(filters.to_creation_date))
            if filters.from_update_date:
                stmt = stmt.where(DBWorkspace.created_at >= normalize_timestamps_to_utc(filters.from_update_date))
            if filters.to_update_date:
                stmt = stmt.where(DBWorkspace.created_at <= normalize_timestamps_to_utc(filters.to_update_date))
            return stmt

        total_stmt = select(func.count()).select_from(DBWorkspace)
        total_stmt = _apply_filters(stmt=total_stmt)
        total: int = (await session.execute(total_stmt)).scalar_one()
        stmt = select(DBWorkspace)
        stmt = _apply_filters(stmt=stmt)
        column: Column = getattr(DBWorkspace, filters.order_by)
        stmt = stmt.order_by(column.desc() if filters.order == "desc" else column.asc())
        if filters.limit is not None:
            stmt = stmt.limit(filters.limit)
        if filters.offset is not None:
            stmt = stmt.offset(filters.offset)
        result = await session.execute(stmt)
        db_workspaces: list[DBWorkspace] = result.scalars().all()
        return db_workspaces, total

    @staticmethod
    async def update_by_id(session: AsyncSession, id: UUID, params: UpdateWorkspaceRequest) -> DBWorkspace:
        stmt = (
            update(DBWorkspace)
            .where(DBWorkspace.id == id)
            .values(**params.model_dump(exclude_unset=True))
            .returning(DBWorkspace)
        )
        result: Result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def delete_by_id(session: AsyncSession, id: UUID) -> UUID | None:
        stmt = delete(DBWorkspace).where(DBWorkspace.id == id).returning(DBWorkspace.id)
        result: Result = await session.execute(stmt)
        return result.scalar_one_or_none()
