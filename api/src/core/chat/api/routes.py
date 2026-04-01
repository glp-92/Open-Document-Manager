import traceback
from typing import Annotated
from uuid import UUID

from core.chat.api.dto.requests import ChatFilters, NewChatRequest
from core.chat.api.dto.responses import ChatListResponse, ChatResponse
from core.chat.application.service import ChatService
from core.chat.exceptions.chat import ChatNotFoundError
from db.sql_alchemy_unit_of_work import get_db
from fastapi import APIRouter, Depends, Query
from fastapi.exceptions import HTTPException
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession


class ChatRouter:
    router = APIRouter()

    def __init__(self, chat_service: ChatService):
        self.chat_service = chat_service
        self._register_routes()

    def _register_routes(self):
        @self.router.get("", status_code=200, response_model=ChatListResponse)
        async def find_chats_with_filters_pageable(
            filters: Annotated[ChatFilters, Query()], sql_session: AsyncSession = Depends(get_db)
        ):
            try:
                return await self.chat_service.find_chats_with_filters_pageable(session=sql_session, filters=filters)
            except (ValidationError, Exception):
                traceback.print_exc()
                raise HTTPException(status_code=400, detail="bad request")

        @self.router.post("", status_code=201, response_model=ChatResponse)
        async def create_chat(new_chat_request: NewChatRequest, sql_session: AsyncSession = Depends(get_db)):
            try:
                return await self.chat_service.create_chat(session=sql_session, new_chat_request=new_chat_request)
            except (ValidationError, Exception):
                traceback.print_exc()
                raise HTTPException(status_code=400, detail="bad request")

        @self.router.delete("/{chat_id}", status_code=204)
        async def delete_chat(chat_id: UUID, sql_session: AsyncSession = Depends(get_db)):
            try:
                return await self.chat_service.delete_chat_by_id(session=sql_session, chat_id=chat_id)
            except ChatNotFoundError:
                raise HTTPException(status_code=404, detail="not found")
            except (ValidationError, Exception):
                traceback.print_exc()
                raise HTTPException(status_code=400, detail="bad request")
