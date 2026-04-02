import traceback
from typing import Annotated
from uuid import UUID

from core.document.api.dto.requests import DocumentFilters, DocumentStorageWebhookRequest, NewDocumentRequest
from core.document.api.dto.responses import (
    DocumentListResponse,
    DocumentStorageWebhookResponse,
    UploadDocumentOptimisticResponse,
)
from core.document.application.service import DocumentService
from core.document.exceptions.document import DocumentNotFoundError
from db.sql_alchemy_unit_of_work import get_db
from fastapi import APIRouter, Depends, Query
from fastapi.exceptions import HTTPException
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from storage.s3_adapter import S3Adapter, get_storage


class DocumentRouter:
    router = APIRouter()

    def __init__(self, document_service: DocumentService):
        self.document_service = document_service
        self._register_routes()

    def _register_routes(self):
        @self.router.get("", status_code=200, response_model=DocumentListResponse)
        async def find_documents_with_filters_pageable(
            filters: Annotated[DocumentFilters, Query()], sql_session: AsyncSession = Depends(get_db)
        ):
            try:
                return await self.document_service.find_documents_with_filters_pageable(
                    session=sql_session, filters=filters
                )
            except (ValidationError, Exception):
                traceback.print_exc()
                raise HTTPException(status_code=400, detail="bad request")

        @self.router.post("", status_code=201, response_model=UploadDocumentOptimisticResponse)
        async def create_document(
            new_document_request: NewDocumentRequest,
            sql_session: AsyncSession = Depends(get_db),
            s3_adapter: S3Adapter = Depends(get_storage),
        ):
            try:
                return await self.document_service.create_document(
                    session=sql_session, storage_adapter=s3_adapter, new_document_request=new_document_request
                )
            except (ValidationError, Exception):
                traceback.print_exc()
                raise HTTPException(status_code=400, detail="bad request")

        @self.router.post("/webhooks", status_code=200, response_model=DocumentStorageWebhookResponse)
        async def process_webhooks_from_storage(
            request: DocumentStorageWebhookRequest,
            sql_session: AsyncSession = Depends(get_db),
        ):
            try:
                return await self.document_service.process_storage_webhooks(session=sql_session, request=request)
            except DocumentNotFoundError:
                raise HTTPException(status_code=404, detail="not found")
            except (ValidationError, Exception):
                traceback.print_exc()
                raise HTTPException(status_code=400, detail="bad request")

        @self.router.delete("/{document_id}", status_code=204)
        async def delete_document(document_id: UUID, sql_session: AsyncSession = Depends(get_db)):
            try:
                return await self.document_service.delete_document_by_id(session=sql_session, document_id=document_id)
            except DocumentNotFoundError:
                raise HTTPException(status_code=404, detail="not found")
            except (ValidationError, Exception):
                traceback.print_exc()
                raise HTTPException(status_code=400, detail="bad request")
