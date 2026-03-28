from uuid import UUID

from core.workspace.api.dto.requests import NewWorkspaceRequest, WorkspaceFilters
from core.workspace.api.dto.responses import WorkspaceListResponse, WorkspaceResponse
from core.workspace.domain.model import Workspace
from core.workspace.exceptions.workspace import WorkspaceNotFoundError
from core.workspace.infrastructure.db_model import DBWorkspace
from core.workspace.infrastructure.repository_impl import WorkspaceRepositoryImpl
from sqlalchemy.orm import Session


class WorkspaceService:
    def __init__(self, workspace_repository_impl: WorkspaceRepositoryImpl):
        self.workspace_repository_impl = workspace_repository_impl

    def create_workspace(self, session: Session, new_workspace_request: NewWorkspaceRequest) -> WorkspaceResponse:
        workspace: Workspace = Workspace(**new_workspace_request.model_dump())
        return WorkspaceResponse.model_validate(
            self.workspace_repository_impl.save(session=session, workspace=workspace), from_attributes=True
        )

    def find_workspaces_with_filters_pageable(
        self, session: Session, filters: WorkspaceFilters
    ) -> WorkspaceListResponse:
        db_workspaces: list[DBWorkspace] = []
        total: int = 0
        db_workspaces, total = self.workspace_repository_impl.find_many_filtered_pageable(
            session=session, filters=filters
        )
        return WorkspaceListResponse(
            workspaces=[
                WorkspaceResponse.model_validate(obj=db_workspace, from_attributes=True)
                for db_workspace in db_workspaces
            ],
            total=total,
        )

    def delete_workspace_by_id(self, session: Session, workspace_id: UUID):
        deleted: bool = self.workspace_repository_impl.delete_by_id(session=session, id=workspace_id)
        if not deleted:
            raise WorkspaceNotFoundError(workspace_id=workspace_id)
        return
