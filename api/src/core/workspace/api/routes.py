import traceback

from core.workspace.api.dto.requests import NewWorkspaceRequest
from core.workspace.api.dto.responses import WorkspaceResponse
from core.workspace.application.service import WorkspaceService
from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from pydantic import ValidationError


class WorkspaceRouter:
    router = APIRouter()

    def __init__(self, workspace_service: WorkspaceService):
        self.workspace_service = workspace_service
        self._register_routes()

    def _register_routes(self):
        @self.router.post("", status_code=201, response_model=WorkspaceResponse)
        async def create_workspace(
            new_workspace_request: NewWorkspaceRequest,
        ):
            try:
                return self.workspace_service.create_workspace(new_workspace_request=new_workspace_request)
            except (ValidationError, Exception):
                traceback.print_exc()
                raise HTTPException(status_code=400, detail="bad request")
