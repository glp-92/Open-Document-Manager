from uuid import UUID

from core.document.api.dto.requests import DocumentFilters, NewDocumentRequest
from core.document.api.dto.responses import DocumentListResponse, DocumentResponse
from core.document.domain.model import Document
from core.document.exceptions.document import DocumentNotFoundError
from core.document.infrastructure.db_model import DBDocument
from core.document.infrastructure.repository_impl import DocumentRepositoryImpl
from sqlalchemy.orm import Session


class DocumentService:
    def __init__(self, document_repository_impl: DocumentRepositoryImpl):
        self.document_repository_impl = document_repository_impl

    async def create_document(self, session: Session, new_document_request: NewDocumentRequest) -> DocumentResponse:
        document: Document = Document(**new_document_request.model_dump())
        db_document = await self.document_repository_impl.save(session=session, document=document)
        return DocumentResponse.model_validate(db_document, from_attributes=True)

    async def find_documents_with_filters_pageable(
        self, session: Session, filters: DocumentFilters
    ) -> DocumentListResponse:
        db_documents: list[DBDocument] = []
        total: int = 0
        db_documents, total = await self.document_repository_impl.find_many_filtered_pageable(
            session=session, filters=filters
        )
        return DocumentListResponse(
            documents=[
                DocumentResponse.model_validate(obj=db_document, from_attributes=True) for db_document in db_documents
            ],
            total=total,
        )

    async def delete_document_by_id(self, session: Session, document_id: UUID):
        deleted_id: UUID | None = await self.document_repository_impl.delete_by_id(session=session, id=document_id)
        if deleted_id is None:
            raise DocumentNotFoundError(workspace_id=document_id)
        return
