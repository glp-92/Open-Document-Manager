from uuid import UUID

from config.config import config
from config.logger import logger
from core.document.api.dto.requests import (
    DocumentFilters,
    DocumentStorageWebhookEntry,
    DocumentStorageWebhookRequest,
    NewDocumentRequest,
)
from core.document.api.dto.responses import (
    DocumentListResponse,
    DocumentResponse,
    DocumentStorageWebhookResponse,
    UploadDocumentOptimisticResponse,
)
from core.document.domain.model import Document, StorageStatus
from core.document.exceptions.document import DocumentNotFoundError
from core.document.infrastructure.db_model import DBDocument
from core.document.infrastructure.repository_impl import DocumentRepositoryImpl
from sqlalchemy.ext.asyncio import AsyncSession
from storage.s3_adapter import S3Adapter


class DocumentService:
    def __init__(self, document_repository_impl: DocumentRepositoryImpl):
        self.document_repository_impl = document_repository_impl

    async def create_document(
        self, session: AsyncSession, storage_adapter: S3Adapter, new_document_request: NewDocumentRequest
    ) -> UploadDocumentOptimisticResponse:
        document: Document = Document(**new_document_request.model_dump())
        db_document = await self.document_repository_impl.save(session=session, document=document)
        presigned_url: str = storage_adapter.get_upload_url(
            bucket=config.storage_bucket,
            filename=new_document_request.filename,
            id=db_document.id,
            expires_in=config.storage_presigned_url_expiration,
        )
        return UploadDocumentOptimisticResponse(
            id=db_document.id,
            workspace_id=db_document.workspace_id,
            filename=db_document.filename,
            presigned_url=presigned_url,
            created_at=db_document.created_at,
        )

    async def find_documents_with_filters_pageable(
        self, session: AsyncSession, filters: DocumentFilters
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

    async def _on_create(self, session: AsyncSession, document_id: UUID, key: str, entry: DocumentStorageWebhookEntry):
        db_document: DBDocument = await self.document_repository_impl.find_by_id(session=session, id=document_id)
        if db_document is None:
            raise DocumentNotFoundError(document_id=document_id)
        db_document.url = key
        db_document.filename = entry.name
        db_document.size = entry.attributes.file_size
        db_document.mime = entry.attributes.mime
        db_document.storage_status = StorageStatus.READY
        return

    async def _on_rename(self, session: AsyncSession, document_id: UUID, key: str, entry: DocumentStorageWebhookEntry):
        db_document: DBDocument = await self.document_repository_impl.find_by_id(session=session, id=document_id)
        if db_document is None:
            raise DocumentNotFoundError(document_id=document_id)
        db_document.url = key
        db_document.filename = entry.name
        return

    async def _filter_folder_creation_events(self, request: DocumentStorageWebhookRequest) -> bool:
        if request.message.new_entry and request.message.new_entry.is_directory:
            logger.info("received webhook for a directory creation event, ignoring.")
            return True
        return False

    async def process_storage_webhooks(
        self, session: AsyncSession, request: DocumentStorageWebhookRequest
    ) -> DocumentStorageWebhookResponse:
        if await self._filter_folder_creation_events(request):
            return DocumentStorageWebhookResponse(status="ok")
        document_id: UUID = UUID(request.key.strip("/").split("/")[-2])
        match request.event_type:
            case "create":
                logger.info("upload event received from storage")
                await self._on_create(
                    session=session, document_id=document_id, key=request.key, entry=request.message.new_entry
                )
            case "delete":
                logger.info("delete event received from storage")
                try:
                    await self.delete_document_by_id(session=session, document_id=document_id)
                except DocumentNotFoundError:
                    logger.info(
                        "delete webhook ignored for already deleted document id=%s",
                        document_id,
                    )
            case "rename":
                logger.info("rename event received from storage")
                await self._on_rename(
                    session=session, document_id=document_id, key=request.key, entry=request.message.old_entry
                )
            case _:
                pass
        return DocumentStorageWebhookResponse(status="ok")

    async def delete_document_by_id(
        self,
        session: AsyncSession,
        document_id: UUID,
        storage_adapter: S3Adapter | None = None,
    ) -> None:
        document_url: str | None = await self.document_repository_impl.delete_by_id(session=session, id=document_id)
        if document_url is None:
            raise DocumentNotFoundError(document_id=document_id)
        if storage_adapter is not None:
            await storage_adapter.delete_file(bucket=config.storage_bucket, filename=document_url)
