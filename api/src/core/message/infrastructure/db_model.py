from __future__ import annotations

from core.message.domain.model import Message, Owner
from db.sql_alchemy_unit_of_work import Base
from db.utils import gen_utc_timestamp, gen_uuid
from sqlalchemy import TEXT, Column, DateTime, Enum
from sqlalchemy.dialects.mysql import BINARY


class DBMessage(Base):
    __tablename__ = "messages"

    id = Column(BINARY(16), primary_key=True, default=gen_uuid)
    owner = Column(Enum(Owner), nullable=False)
    content = Column(TEXT, nullable=False)
    created_at = Column(DateTime, nullable=True, default=gen_utc_timestamp)
    updated_at = Column(
        DateTime,
        nullable=True,
        default=gen_utc_timestamp,
        onupdate=gen_utc_timestamp,
    )

    @staticmethod
    def to_domain_object(db_message: DBMessage) -> Message:
        return Message.model_validate(db_message, from_attributes=True)

    @staticmethod
    def from_domain_object(message: Message) -> DBMessage:
        return DBMessage(**message.model_dump(exclude_none=True))
