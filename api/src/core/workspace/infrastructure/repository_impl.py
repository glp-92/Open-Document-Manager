from uuid import UUID

from core.workspace.api.dto.requests import WorkspaceFilters
from core.workspace.domain.model import Workspace
from core.workspace.domain.repository import WorkspaceRepository
from core.workspace.infrastructure.db_model import DBWorkspace
from sqlalchemy import Column, Result, Select, delete, func, select
from sqlalchemy.orm import Session


class WorkspaceRepositoryImpl(WorkspaceRepository):
    def __init__(self):
        return

    @staticmethod
    def save(session: Session, workspace: Workspace) -> DBWorkspace:
        db_workspace: DBWorkspace = DBWorkspace.from_domain_object(workspace=workspace)
        session.add(db_workspace)
        session.flush()
        return db_workspace

    @staticmethod
    def find_many_filtered_pageable(session: Session, filters: WorkspaceFilters) -> tuple[list[DBWorkspace], int]:
        def _apply_filters(stmt: Select):
            if filters.name:
                stmt = stmt.where(DBWorkspace.name.contains(filters.name))
            return stmt

        total_stmt = select(func.count()).select_from(DBWorkspace)
        total_stmt = _apply_filters(stmt=total_stmt)
        total: int = session.execute(total_stmt).scalar_one()
        stmt = select(DBWorkspace)
        stmt = _apply_filters(stmt=stmt)
        column: Column = getattr(DBWorkspace, filters.order_by)
        stmt = stmt.order_by(column.desc() if filters.order == "desc" else column.asc())
        if filters.limit is not None:
            stmt = stmt.limit(filters.limit)
        if filters.offset is not None:
            stmt = stmt.offset(filters.offset)
        result = session.execute(stmt)
        db_workspaces: list[DBWorkspace] = result.scalars().all()
        return db_workspaces, total

    @staticmethod
    def delete_by_id(session: Session, id: UUID) -> bool:
        stmt = delete(DBWorkspace).where(DBWorkspace.id == id)
        result: Result = session.execute(stmt)
        return result.rowcount > 0
