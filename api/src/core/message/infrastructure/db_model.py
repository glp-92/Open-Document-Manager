from __future__ import annotations

from uuid import uuid4

from core.chat.infrastructure.db_model import DBChat
from core.message.domain.model import Message, Owner
from db.sql_alchemy_unit_of_work import Base
from sqlalchemy import TEXT, Column, DateTime, Enum, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class DBMessage(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    owner = Column(Enum(Owner, native_enum=False), nullable=False)
    content = Column(TEXT, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=True, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=True, server_default=func.now(), server_onupdate=func.now())
    chat_id = Column(UUID, ForeignKey(DBChat.id, ondelete="CASCADE"), nullable=False)
    chat = relationship("DBChat", back_populates="messages")

    @staticmethod
    def to_domain_object(db_message: DBMessage) -> Message:
        return Message.model_validate(db_message, from_attributes=True)

    @staticmethod
    def from_domain_object(message: Message) -> DBMessage:
        return DBMessage(**message.model_dump(exclude_none=True))
