from __future__ import annotations

from uuid import uuid4

from core.chat.infrastructure.db_model import DBChat
from core.document.domain.model import Document, StorageStatus
from db.sql_alchemy_unit_of_work import Base
from sqlalchemy import INTEGER, Column, DateTime, Enum, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class DBDocument(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    filename = Column(String(100), nullable=False)
    url = Column(String(100), nullable=True)
    size = Column(INTEGER, nullable=True)
    mime = Column(String(50), nullable=True)
    storage_status = Column(Enum(StorageStatus, native_enum=False), nullable=False, default=StorageStatus.PENDING)
    created_at = Column(DateTime(timezone=True), nullable=True, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=True, server_default=func.now(), server_onupdate=func.now())
    chat_id = Column(UUID, ForeignKey(DBChat.id, ondelete="CASCADE"), nullable=False)
    chat = relationship("DBChat", back_populates="documents")

    @staticmethod
    def to_domain_object(db_document: DBDocument) -> Document:
        return Document.model_validate(db_document, from_attributes=True)

    @staticmethod
    def from_domain_object(document: Document) -> DBDocument:
        return DBDocument(**document.model_dump(exclude_none=True))
