from core.workspace.api.routes import WorkspaceRouter
from core.workspace.application.service import WorkspaceService
from core.workspace.infrastructure.repository_impl import WorkspaceRepositoryImpl
from fastapi import FastAPI
from sqlalchemy.orm import Session


class Core:
    app = FastAPI(title="FAIR Application Server")

    def __init__(self, sql_session_factory: Session):
        self.sql_session_factory = sql_session_factory
        self._set_repositories()
        self._set_services()
        self._set_routers()
        self._include_routers_on_app()

    def _set_repositories(self):
        self.workspace_repository_impl = WorkspaceRepositoryImpl

    def _set_services(self):
        self.workspace_service = WorkspaceService(
            sql_session_factory=self.sql_session_factory, workspace_repository_impl=self.workspace_repository_impl
        )

    def _set_routers(self):
        self.workspace_router = WorkspaceRouter(workspace_service=self.workspace_service)

    def _include_routers_on_app(self):
        self.app.include_router(self.workspace_router.router, prefix="/workspaces", tags=["Workspaces"])
