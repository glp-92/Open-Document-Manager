from __future__ import annotations

from core.shared.infrastructure.timestamps import gen_utc_timestamp
from core.shared.infrastructure.uuid import UUID, gen_uuid
from core.workspace.domain.model import Workspace
from db.sql_alchemy_unit_of_work import Base
from sqlalchemy import Column, DateTime, String
from sqlalchemy.orm import relationship


class DBWorkspace(Base):
    __tablename__ = "workspaces"

    id = Column(UUID, primary_key=True, default=gen_uuid)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime, nullable=True, default=gen_utc_timestamp)
    updated_at = Column(
        DateTime,
        nullable=True,
        default=gen_utc_timestamp,
        onupdate=gen_utc_timestamp,
    )
    chats = relationship("DBChat", back_populates="workspace", passive_deletes=True)

    @staticmethod
    def to_domain_object(db_workspace: DBWorkspace) -> Workspace:
        return Workspace.model_validate(db_workspace, from_attributes=True)

    @staticmethod
    def from_domain_object(workspace: Workspace) -> DBWorkspace:
        return DBWorkspace(**workspace.model_dump(exclude_none=True))
