from uuid import UUID

from core.document.api.dto.requests import DocumentFilters
from core.document.domain.model import Document
from core.document.domain.repository import DocumentRepository
from core.document.infrastructure.db_model import DBDocument
from sqlalchemy import Column, Result, Select, delete, func, select
from sqlalchemy.orm import Session


class DocumentRepositoryImpl(DocumentRepository):
    def __init__(self):
        return

    @staticmethod
    def save(session: Session, document: Document) -> DBDocument:
        db_document: DBDocument = DBDocument.from_domain_object(document=document)
        session.add(db_document)
        session.flush()
        return db_document

    @staticmethod
    def find_many_filtered_pageable(session: Session, filters: DocumentFilters) -> tuple[list[DBDocument], int]:
        def _apply_filters(stmt: Select):
            if filters.filename:
                stmt = stmt.where(DBDocument.filename.contains(filters.filename))
            if filters.chat_id:
                stmt = stmt.where(DBDocument.chat_id == filters.chat_id)
            return stmt

        total_stmt = select(func.count()).select_from(DBDocument)
        total_stmt = _apply_filters(stmt=total_stmt)
        total: int = session.execute(total_stmt).scalar_one()
        stmt = select(DBDocument)
        stmt = _apply_filters(stmt=stmt)
        column: Column = getattr(DBDocument, filters.order_by)
        stmt = stmt.order_by(column.desc() if filters.order == "desc" else column.asc())
        if filters.limit is not None:
            stmt = stmt.limit(filters.limit)
        if filters.offset is not None:
            stmt = stmt.offset(filters.offset)
        result = session.execute(stmt)
        db_documents: list[DBDocument] = result.scalars().all()
        return db_documents, total

    @staticmethod
    def delete_by_id(session: Session, id: UUID) -> bool:
        stmt = delete(DBDocument).where(DBDocument.id == id)
        result: Result = session.execute(stmt)
        return result.rowcount > 0
