import traceback
from typing import Annotated
from uuid import UUID

from core.message.api.dto.requests import MessageFilters, NewMessageRequest
from core.message.api.dto.responses import MessageListResponse, MessageResponse
from core.message.application.service import MessageService
from core.message.exceptions.workspace import MessageNotFoundError
from db.sql_alchemy_unit_of_work import get_db
from fastapi import APIRouter, Depends, Query
from fastapi.exceptions import HTTPException
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession


class MessageRouter:
    router = APIRouter()

    def __init__(self, message_service: MessageService):
        self.message_service = message_service
        self._register_routes()

    def _register_routes(self):
        @self.router.get("", status_code=200, response_model=MessageListResponse)
        async def find_messages_with_filters_pageable(
            filters: Annotated[MessageFilters, Query()], sql_session: AsyncSession = Depends(get_db)
        ):
            try:
                return await self.message_service.find_messages_with_filters_pageable(
                    session=sql_session, filters=filters
                )
            except (ValidationError, Exception):
                traceback.print_exc()
                raise HTTPException(status_code=400, detail="bad request")

        @self.router.post("", status_code=201, response_model=MessageResponse)
        async def create_message(new_message_request: NewMessageRequest, sql_session: AsyncSession = Depends(get_db)):
            try:
                return await self.message_service.create_message(
                    session=sql_session, new_message_request=new_message_request
                )
            except (ValidationError, Exception):
                traceback.print_exc()
                raise HTTPException(status_code=400, detail="bad request")

        @self.router.delete("/{message_id}", status_code=204)
        async def delete_message(message_id: UUID, sql_session: AsyncSession = Depends(get_db)):
            try:
                return await self.message_service.delete_message_by_id(session=sql_session, message_id=message_id)
            except MessageNotFoundError:
                raise HTTPException(status_code=404, detail="not found")
            except (ValidationError, Exception):
                traceback.print_exc()
                raise HTTPException(status_code=400, detail="bad request")
