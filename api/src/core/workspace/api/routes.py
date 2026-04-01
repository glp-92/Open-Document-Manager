import traceback
from typing import Annotated
from uuid import UUID

from core.workspace.api.dto.requests import NewWorkspaceRequest, WorkspaceFilters
from core.workspace.api.dto.responses import WorkspaceListResponse, WorkspaceResponse
from core.workspace.application.service import WorkspaceService
from core.workspace.exceptions.workspace import WorkspaceNotFoundError
from db.sql_alchemy_unit_of_work import get_db
from fastapi import APIRouter, Depends, Query
from fastapi.exceptions import HTTPException
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession


class WorkspaceRouter:
    router = APIRouter()

    def __init__(self, workspace_service: WorkspaceService):
        self.workspace_service = workspace_service
        self._register_routes()

    def _register_routes(self):
        @self.router.get("", status_code=200, response_model=WorkspaceListResponse)
        async def find_workspaces_with_filters_pageable(
            filters: Annotated[WorkspaceFilters, Query()], sql_session: AsyncSession = Depends(get_db)
        ):
            try:
                return await self.workspace_service.find_workspaces_with_filters_pageable(
                    session=sql_session, filters=filters
                )
            except (ValidationError, Exception):
                traceback.print_exc()
                raise HTTPException(status_code=400, detail="bad request")

        @self.router.post("", status_code=201, response_model=WorkspaceResponse)
        async def create_workspace(
            new_workspace_request: NewWorkspaceRequest, sql_session: AsyncSession = Depends(get_db)
        ):
            try:
                return await self.workspace_service.create_workspace(
                    session=sql_session, new_workspace_request=new_workspace_request
                )
            except (ValidationError, Exception):
                traceback.print_exc()
                raise HTTPException(status_code=400, detail="bad request")

        @self.router.delete("/{workspace_id}", status_code=204)
        async def delete_workspace(workspace_id: UUID, sql_session: AsyncSession = Depends(get_db)):
            try:
                return await self.workspace_service.delete_workspace_by_id(
                    session=sql_session, workspace_id=workspace_id
                )
            except WorkspaceNotFoundError:
                raise HTTPException(status_code=404, detail="not found")
            except (ValidationError, Exception):
                traceback.print_exc()
                raise HTTPException(status_code=400, detail="bad request")
