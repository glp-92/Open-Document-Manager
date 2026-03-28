from abc import ABC, abstractmethod

from core.chat.api.dto.requests import ChatFilters
from core.chat.domain.model import Chat
from core.chat.infrastructure.db_model import DBChat
from sqlalchemy.orm import Session


class ChatRepository(ABC):
    @abstractmethod
    def save(self, session: Session, chat: Chat) -> DBChat:
        pass

    @abstractmethod
    def find_many_filtered_pageable(self, session: Session, filters: ChatFilters) -> tuple[list[DBChat], int]:
        pass
