from uuid import UUID

from core.chat.api.dto.requests import ChatFilters
from core.chat.domain.model import Chat
from core.chat.domain.repository import ChatRepository
from core.chat.infrastructure.db_model import DBChat
from sqlalchemy import Column, Result, Select, delete, func, select
from sqlalchemy.orm import Session


class ChatRepositoryImpl(ChatRepository):
    def __init__(self):
        return

    @staticmethod
    def save(session: Session, chat: Chat) -> DBChat:
        db_chat: DBChat = DBChat.from_domain_object(chat=chat)
        session.add(db_chat)
        session.flush()
        return db_chat

    @staticmethod
    def find_many_filtered_pageable(session: Session, filters: ChatFilters) -> tuple[list[DBChat], int]:
        def _apply_filters(stmt: Select):
            if filters.name:
                stmt = stmt.where(DBChat.name.contains(filters.name))
            return stmt

        total_stmt = select(func.count()).select_from(DBChat)
        total_stmt = _apply_filters(stmt=total_stmt)
        total: int = session.execute(total_stmt).scalar_one()
        stmt = select(DBChat)
        stmt = _apply_filters(stmt=stmt)
        column: Column = getattr(DBChat, filters.order_by)
        stmt = stmt.order_by(column.desc() if filters.order == "desc" else column.asc())
        if filters.limit is not None:
            stmt = stmt.limit(filters.limit)
        if filters.offset is not None:
            stmt = stmt.offset(filters.offset)
        result = session.execute(stmt)
        db_chats: list[DBChat] = result.scalars().all()
        return db_chats, total

    @staticmethod
    def delete_by_id(session: Session, id: UUID) -> bool:
        stmt = delete(DBChat).where(DBChat.id == id)
        result: Result = session.execute(stmt)
        return result.rowcount > 0
