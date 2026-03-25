from core.workspace.api.dto.requests import NewWorkspaceRequest
from core.workspace.api.dto.responses import WorkspaceResponse
from core.workspace.domain.model import Workspace
from core.workspace.infrastructure.repository_impl import WorkspaceRepositoryImpl
from sqlalchemy.orm import Session


class WorkspaceService:
    def __init__(self, sql_session_factory: Session, workspace_repository_impl: WorkspaceRepositoryImpl):
        self.sql_session_factory = sql_session_factory
        self.workspace_repository_impl = workspace_repository_impl

    def create_workspace(self, new_workspace_request: NewWorkspaceRequest) -> WorkspaceResponse:
        with self.sql_session_factory() as session:
            workspace: Workspace = Workspace(**new_workspace_request.model_dump())
            return WorkspaceResponse.model_validate(
                self.workspace_repository_impl.save(session=session, workspace=workspace), from_attributes=True
            )
