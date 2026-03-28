import traceback
from typing import Annotated

from core.workspace.api.dto.requests import NewWorkspaceRequest, WorkspaceFilters
from core.workspace.api.dto.responses import WorkspaceListResponse, WorkspaceResponse
from core.workspace.application.service import WorkspaceService
from db.sql_alchemy_unit_of_work import SqlAlchemyUnitOfWork, get_db
from fastapi import APIRouter, Depends, Query
from fastapi.exceptions import HTTPException
from pydantic import ValidationError


class WorkspaceRouter:
    router = APIRouter()

    def __init__(self, workspace_service: WorkspaceService):
        self.workspace_service = workspace_service
        self._register_routes()

    def _register_routes(self):
        @self.router.get("", status_code=200, response_model=WorkspaceListResponse)
        async def find_workspaces_with_filters_pageable(
            filters: Annotated[WorkspaceFilters, Query()], uow: SqlAlchemyUnitOfWork = Depends(get_db)
        ):
            try:
                return self.workspace_service.find_workspaces_with_filters_pageable(
                    session=uow.session, filters=filters
                )
            except (ValidationError, Exception):
                traceback.print_exc()
                raise HTTPException(status_code=400, detail="bad request")

        @self.router.post("", status_code=201, response_model=WorkspaceResponse)
        async def create_workspace(
            new_workspace_request: NewWorkspaceRequest, uow: SqlAlchemyUnitOfWork = Depends(get_db)
        ):
            try:
                return self.workspace_service.create_workspace(
                    session=uow.session, new_workspace_request=new_workspace_request
                )
            except (ValidationError, Exception):
                traceback.print_exc()
                raise HTTPException(status_code=400, detail="bad request")
