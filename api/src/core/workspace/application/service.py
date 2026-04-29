from uuid import UUID

from config.config import config
from config.logger import logger
from core.document.infrastructure.repository_impl import DocumentRepositoryImpl
from core.workspace.api.dto.requests import NewWorkspaceRequest, UpdateWorkspaceRequest, WorkspaceFilters
from core.workspace.api.dto.responses import WorkspaceListResponse, WorkspaceResponse
from core.workspace.domain.model import Workspace
from core.workspace.exceptions.workspace import WorkspaceNotFoundError
from core.workspace.infrastructure.db_model import DBWorkspace
from core.workspace.infrastructure.repository_impl import WorkspaceRepositoryImpl
from sqlalchemy.ext.asyncio import AsyncSession
from storage.s3_adapter import S3Adapter


class WorkspaceService:
    def __init__(
        self,
        workspace_repository_impl: WorkspaceRepositoryImpl,
        document_repository_impl: DocumentRepositoryImpl,
    ):
        self.workspace_repository_impl = workspace_repository_impl
        self.document_repository_impl = document_repository_impl

    async def create_workspace(
        self, session: AsyncSession, new_workspace_request: NewWorkspaceRequest
    ) -> WorkspaceResponse:
        workspace: Workspace = Workspace(**new_workspace_request.model_dump())
        db_workspace: DBWorkspace = await self.workspace_repository_impl.save(session=session, workspace=workspace)
        return WorkspaceResponse.model_validate(db_workspace, from_attributes=True)

    async def find_workspaces_with_filters_pageable(
        self, session: AsyncSession, filters: WorkspaceFilters
    ) -> WorkspaceListResponse:
        db_workspaces: list[DBWorkspace] = []
        total: int = 0
        db_workspaces, total = await self.workspace_repository_impl.find_many_filtered_pageable(
            session=session, filters=filters
        )
        return WorkspaceListResponse(
            workspaces=[
                WorkspaceResponse.model_validate(obj=db_workspace, from_attributes=True)
                for db_workspace in db_workspaces
            ],
            total=total,
        )

    async def edit_workspace(
        self, session: AsyncSession, workspace_id: UUID, update_workspace_request: UpdateWorkspaceRequest
    ) -> WorkspaceResponse:
        db_workspace: DBWorkspace | None = await self.workspace_repository_impl.update_by_id(
            session=session, id=workspace_id, params=update_workspace_request
        )
        if db_workspace is None:
            raise WorkspaceNotFoundError(workspace_id=workspace_id)
        return WorkspaceResponse.model_validate(db_workspace, from_attributes=True)

    async def delete_workspace_by_id(
        self,
        session: AsyncSession,
        workspace_id: UUID,
        storage_adapter: S3Adapter | None = None,
    ):
        document_urls = await self.document_repository_impl.find_urls_by_workspace_id(
            session=session,
            workspace_id=workspace_id,
        )
        deleted_id: UUID | None = await self.workspace_repository_impl.delete_by_id(session=session, id=workspace_id)
        if deleted_id is None:
            raise WorkspaceNotFoundError(workspace_id=workspace_id)
        if storage_adapter is None:
            return
        for document_url in document_urls:
            try:
                await storage_adapter.delete_file(bucket=config.storage_bucket, filename=document_url)
            except Exception:
                logger.exception(
                    "failed to delete S3 object for workspace_id=%s url=%s",
                    workspace_id,
                    document_url,
                )
        return
