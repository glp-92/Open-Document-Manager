from __future__ import annotations

from uuid import uuid4

from core.workspace.domain.model import Workspace
from db.sql_alchemy_unit_of_work import Base
from sqlalchemy import Column, DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class DBWorkspace(Base):
    __tablename__ = "workspaces"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=True, server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        nullable=True,
        server_default=func.now(),
        server_onupdate=func.now(),
    )
    chats = relationship("DBChat", back_populates="workspace", passive_deletes=True)
    documents = relationship("DBDocument", back_populates="workspace", passive_deletes=True)
    runs = relationship("DBRun", back_populates="workspace", passive_deletes=True)

    @staticmethod
    def to_domain_object(db_workspace: DBWorkspace) -> Workspace:
        return Workspace.model_validate(db_workspace, from_attributes=True)

    @staticmethod
    def from_domain_object(workspace: Workspace) -> DBWorkspace:
        return DBWorkspace(**workspace.model_dump(exclude_none=True))
