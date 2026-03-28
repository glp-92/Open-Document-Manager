from __future__ import annotations

from core.chat.infrastructure.db_model import DBChat
from core.message.domain.model import Message, Owner
from core.shared.infrastructure.timestamps import gen_utc_timestamp
from core.shared.infrastructure.uuid import UUID, gen_uuid
from db.sql_alchemy_unit_of_work import Base
from sqlalchemy import TEXT, Column, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship


class DBMessage(Base):
    __tablename__ = "messages"

    id = Column(UUID, primary_key=True, default=gen_uuid)
    owner = Column(Enum(Owner), nullable=False)
    content = Column(TEXT, nullable=False)
    created_at = Column(DateTime, nullable=True, default=gen_utc_timestamp)
    updated_at = Column(
        DateTime,
        nullable=True,
        default=gen_utc_timestamp,
        onupdate=gen_utc_timestamp,
    )
    chat_id = Column(UUID, ForeignKey(DBChat.id, ondelete="CASCADE"), nullable=False)
    chat = relationship("DBChat", back_populates="messages")

    @staticmethod
    def to_domain_object(db_message: DBMessage) -> Message:
        return Message.model_validate(db_message, from_attributes=True)

    @staticmethod
    def from_domain_object(message: Message) -> DBMessage:
        return DBMessage(**message.model_dump(exclude_none=True))
