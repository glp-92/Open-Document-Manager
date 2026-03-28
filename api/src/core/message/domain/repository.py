from abc import ABC, abstractmethod

from core.message.api.dto.requests import MessageFilters
from core.message.domain.model import Message
from core.message.infrastructure.db_model import DBMessage
from sqlalchemy.orm import Session


class MessageRepository(ABC):
    @abstractmethod
    def save(self, session: Session, Message: Message) -> DBMessage:
        pass

    @abstractmethod
    def find_many_filtered_pageable(self, session: Session, filters: MessageFilters) -> tuple[list[DBMessage], int]:
        pass
