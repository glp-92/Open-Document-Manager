from core.chat.api.dto.requests import ChatFilters, NewChatRequest
from core.chat.api.dto.responses import ChatListResponse, ChatResponse
from core.chat.domain.model import Chat
from core.chat.infrastructure.db_model import DBChat
from core.chat.infrastructure.repository_impl import ChatRepositoryImpl
from sqlalchemy.orm import Session


class ChatService:
    def __init__(self, chat_repository_impl: ChatRepositoryImpl):
        self.chat_repository_impl = chat_repository_impl

    def create_chat(self, session: Session, new_chat_request: NewChatRequest) -> ChatResponse:
        chat: Chat = Chat(**new_chat_request.model_dump())
        return ChatResponse.model_validate(
            self.chat_repository_impl.save(session=session, chat=chat), from_attributes=True
        )

    def find_chats_with_filters_pageable(self, session: Session, filters: ChatFilters) -> ChatListResponse:
        db_chats: list[DBChat] = []
        total: int = 0
        db_chats, total = self.chat_repository_impl.find_many_filtered_pageable(session=session, filters=filters)
        return ChatListResponse(
            chats=[ChatResponse.model_validate(obj=db_chat, from_attributes=True) for db_chat in db_chats],
            total=total,
        )
