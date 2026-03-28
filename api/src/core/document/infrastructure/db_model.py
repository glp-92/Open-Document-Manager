from __future__ import annotations

from core.chat.infrastructure.db_model import DBChat
from core.document.domain.model import Document
from core.shared.infrastructure.timestamps import gen_utc_timestamp
from core.shared.infrastructure.uuid import UUID, gen_uuid
from db.sql_alchemy_unit_of_work import Base
from sqlalchemy import INTEGER, Column, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship


class DBDocument(Base):
    __tablename__ = "documents"

    id = Column(UUID, primary_key=True, default=gen_uuid)
    filename = Column(String(100), nullable=False)
    url = Column(String(100), nullable=True)
    size = Column(INTEGER, nullable=True)
    created_at = Column(DateTime, nullable=True, default=gen_utc_timestamp)
    updated_at = Column(
        DateTime,
        nullable=True,
        default=gen_utc_timestamp,
        onupdate=gen_utc_timestamp,
    )
    chat_id = Column(UUID, ForeignKey(DBChat.id, ondelete="CASCADE"), nullable=False)
    chat = relationship("DBChat", back_populates="documents")

    @staticmethod
    def to_domain_object(db_document: DBDocument) -> Document:
        return Document.model_validate(db_document, from_attributes=True)

    @staticmethod
    def from_domain_object(document: Document) -> DBDocument:
        return DBDocument(**document.model_dump(exclude_none=True))
