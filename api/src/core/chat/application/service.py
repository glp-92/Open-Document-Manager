from uuid import UUID

from core.chat.api.dto.requests import ChatFilters, NewChatRequest
from core.chat.api.dto.responses import ChatListResponse, ChatResponse
from core.chat.domain.model import Chat
from core.chat.exceptions.chat import ChatNotFoundError
from core.chat.infrastructure.db_model import DBChat
from core.chat.infrastructure.repository_impl import ChatRepositoryImpl
from sqlalchemy.ext.asyncio import AsyncSession


class ChatService:
    def __init__(self, chat_repository_impl: ChatRepositoryImpl):
        self.chat_repository_impl = chat_repository_impl

    async def create_chat(self, session: AsyncSession, new_chat_request: NewChatRequest) -> ChatResponse:
        chat: Chat = Chat(**new_chat_request.model_dump())
        db_chat: DBChat = await self.chat_repository_impl.save(session=session, chat=chat)
        return ChatResponse.model_validate(db_chat, from_attributes=True)

    async def find_chats_with_filters_pageable(self, session: AsyncSession, filters: ChatFilters) -> ChatListResponse:
        db_chats: list[DBChat] = []
        total: int = 0
        db_chats, total = await self.chat_repository_impl.find_many_filtered_pageable(session=session, filters=filters)
        return ChatListResponse(
            chats=[ChatResponse.model_validate(obj=db_chat, from_attributes=True) for db_chat in db_chats],
            total=total,
        )

    async def delete_chat_by_id(self, session: AsyncSession, chat_id: UUID):
        deleted_id: UUID | None = await self.chat_repository_impl.delete_by_id(session=session, id=chat_id)
        if deleted_id is None:
            raise ChatNotFoundError(workspace_id=chat_id)
        return
