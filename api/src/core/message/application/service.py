from core.message.api.dto.requests import MessageFilters, NewMessageRequest
from core.message.api.dto.responses import MessageListResponse, MessageResponse
from core.message.domain.model import Message
from core.message.infrastructure.db_model import DBMessage
from core.message.infrastructure.repository_impl import MessageRepositoryImpl
from sqlalchemy.orm import Session


class MessageService:
    def __init__(self, message_repository_impl: MessageRepositoryImpl):
        self.message_repository_impl = message_repository_impl

    def create_message(self, session: Session, new_message_request: NewMessageRequest) -> MessageResponse:
        message: Message = Message(**new_message_request.model_dump())
        return MessageResponse.model_validate(
            self.message_repository_impl.save(session=session, message=message), from_attributes=True
        )

    def find_messages_with_filters_pageable(self, session: Session, filters: MessageFilters) -> MessageListResponse:
        db_messages: list[DBMessage] = []
        total: int = 0
        db_messages, total = self.message_repository_impl.find_many_filtered_pageable(session=session, filters=filters)
        return MessageListResponse(
            messages=[
                MessageResponse.model_validate(obj=db_message, from_attributes=True) for db_message in db_messages
            ],
            total=total,
        )
