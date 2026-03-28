from uuid import UUID

from core.message.api.dto.requests import MessageFilters
from core.message.domain.model import Message
from core.message.domain.repository import MessageRepository
from core.message.infrastructure.db_model import DBMessage
from sqlalchemy import Column, Result, Select, delete, func, select
from sqlalchemy.orm import Session


class MessageRepositoryImpl(MessageRepository):
    def __init__(self):
        return

    @staticmethod
    def save(session: Session, message: Message) -> DBMessage:
        db_message: DBMessage = DBMessage.from_domain_object(message=message)
        session.add(db_message)
        session.flush()
        return db_message

    @staticmethod
    def find_many_filtered_pageable(session: Session, filters: MessageFilters) -> tuple[list[DBMessage], int]:
        def _apply_filters(stmt: Select):
            if filters.owner:
                stmt = stmt.where(DBMessage.owner == filters.owner)
            if filters.content:
                stmt = stmt.where(DBMessage.content.contains(filters.content))
            return stmt

        total_stmt = select(func.count()).select_from(DBMessage)
        total_stmt = _apply_filters(stmt=total_stmt)
        total: int = session.execute(total_stmt).scalar_one()
        stmt = select(DBMessage)
        stmt = _apply_filters(stmt=stmt)
        column: Column = getattr(DBMessage, filters.order_by)
        stmt = stmt.order_by(column.desc() if filters.order == "desc" else column.asc())
        if filters.limit is not None:
            stmt = stmt.limit(filters.limit)
        if filters.offset is not None:
            stmt = stmt.offset(filters.offset)
        result = session.execute(stmt)
        db_messages: list[DBMessage] = result.scalars().all()
        return db_messages, total

    @staticmethod
    def delete_by_id(session: Session, id: UUID) -> bool:
        stmt = delete(DBMessage).where(DBMessage.id == id)
        result: Result = session.execute(stmt)
        return result.rowcount > 0
