from __future__ import annotations

from uuid import uuid4

from core.run.domain.model import Run, Status
from core.workspace.infrastructure.db_model import DBWorkspace
from db.sql_alchemy_unit_of_work import Base
from sqlalchemy import Column, DateTime, Enum, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship


class DBRun(Base):
    __tablename__ = "runs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    status = Column(Enum(Status, native_enum=False), nullable=False, default=Status.PENDING)
    detail = Column(String(length=100), nullable=True)
    meta = Column(JSONB, nullable=True, default={})
    created_at = Column(DateTime(timezone=True), nullable=True, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=True, server_default=func.now(), server_onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    workspace_id = Column(UUID, ForeignKey(DBWorkspace.id, ondelete="CASCADE"), nullable=False)
    workspace = relationship("DBWorkspace", back_populates="runs")

    @staticmethod
    def to_domain_object(db_run: DBRun) -> Run:
        return Run.model_validate(db_run, from_attributes=True)

    @staticmethod
    def from_domain_object(run: Run) -> DBRun:
        return DBRun(**run.model_dump(exclude_none=True))
