import traceback
from typing import Annotated
from uuid import UUID

from core.run.api.dto.requests import NewRunRequest, RunFilters
from core.run.api.dto.responses import (
    RunListResponse,
    RunResponse,
)
from core.run.application.service import RunService
from core.run.exceptions.run import RunNotFoundError
from db.sql_alchemy_unit_of_work import get_db
from fastapi import APIRouter, Depends, Query
from fastapi.exceptions import HTTPException
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession


class RunRouter:
    router = APIRouter()

    def __init__(self, run_service: RunService):
        self.run_service = run_service
        self._register_routes()

    def _register_routes(self):
        @self.router.get("", status_code=200, response_model=RunListResponse)
        async def find_runs_with_filters_pageable(
            filters: Annotated[RunFilters, Query()], sql_session: AsyncSession = Depends(get_db)
        ):
            try:
                return await self.run_service.find_runs_with_filters_pageable(session=sql_session, filters=filters)
            except (ValidationError, Exception):
                traceback.print_exc()
                raise HTTPException(status_code=400, detail="bad request")

        @self.router.post("", status_code=201, response_model=RunResponse)
        async def create_run(
            new_run_request: NewRunRequest,
            sql_session: AsyncSession = Depends(get_db),
        ):
            try:
                return await self.run_service.create_run(session=sql_session, new_run_request=new_run_request)
            except (ValidationError, Exception):
                traceback.print_exc()
                raise HTTPException(status_code=400, detail="bad request")

        @self.router.delete("/{run_id}", status_code=204)
        async def delete_run(run_id: UUID, sql_session: AsyncSession = Depends(get_db)):
            try:
                return await self.run_service.delete_run_by_id(session=sql_session, run_id=run_id)
            except RunNotFoundError:
                raise HTTPException(status_code=404, detail="not found")
            except (ValidationError, Exception):
                traceback.print_exc()
                raise HTTPException(status_code=400, detail="bad request")
