import traceback
from typing import Annotated

from core.chat.api.dto.requests import ChatFilters, NewChatRequest
from core.chat.api.dto.responses import ChatListResponse, ChatResponse
from core.chat.application.service import ChatService
from db.sql_alchemy_unit_of_work import SqlAlchemyUnitOfWork, get_db
from fastapi import APIRouter, Depends, Query
from fastapi.exceptions import HTTPException
from pydantic import ValidationError


class ChatRouter:
    router = APIRouter()

    def __init__(self, chat_service: ChatService):
        self.chat_service = chat_service
        self._register_routes()

    def _register_routes(self):
        @self.router.get("", status_code=200, response_model=ChatListResponse)
        async def find_chats_with_filters_pageable(
            filters: Annotated[ChatFilters, Query()], uow: SqlAlchemyUnitOfWork = Depends(get_db)
        ):
            try:
                return self.chat_service.find_chats_with_filters_pageable(session=uow.session, filters=filters)
            except (ValidationError, Exception):
                traceback.print_exc()
                raise HTTPException(status_code=400, detail="bad request")

        @self.router.post("", status_code=201, response_model=ChatResponse)
        async def create_chat(new_chat_request: NewChatRequest, uow: SqlAlchemyUnitOfWork = Depends(get_db)):
            try:
                return self.chat_service.create_chat(session=uow.session, new_chat_request=new_chat_request)
            except (ValidationError, Exception):
                traceback.print_exc()
                raise HTTPException(status_code=400, detail="bad request")
