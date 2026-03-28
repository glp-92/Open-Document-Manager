from __future__ import annotations

from datetime import datetime

from core.chat.domain.model import Chat
from db.sql_alchemy_unit_of_work import Base
from db.utils import gen_string_timestamp, gen_utc_timestamp, gen_uuid
from sqlalchemy import Column, DateTime, ExecutionContext, String
from sqlalchemy.dialects.mysql import BINARY


def gen_default_name_from_creation_date(context: ExecutionContext):
    created_at_value: datetime | None = context.get_current_parameters().get("created_at")
    if isinstance(created_at_value, datetime):
        return gen_string_timestamp(created_at_value)
    return gen_string_timestamp()


class DBChat(Base):
    __tablename__ = "chats"

    id = Column(BINARY(16), primary_key=True, default=gen_uuid)
    name = Column(String(100), nullable=False, default=gen_default_name_from_creation_date)
    created_at = Column(DateTime, nullable=True, default=gen_utc_timestamp)
    updated_at = Column(
        DateTime,
        nullable=True,
        default=gen_utc_timestamp,
        onupdate=gen_utc_timestamp,
    )

    @staticmethod
    def to_domain_object(db_chat: DBChat) -> Chat:
        return Chat.model_validate(db_chat, from_attributes=True)

    @staticmethod
    def from_domain_object(chat: Chat) -> DBChat:
        return DBChat(**chat.model_dump(exclude_none=True))
