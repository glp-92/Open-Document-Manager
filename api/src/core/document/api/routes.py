import traceback
from typing import Annotated

from core.document.api.dto.requests import DocumentFilters, NewDocumentRequest
from core.document.api.dto.responses import DocumentListResponse, DocumentResponse
from core.document.application.service import DocumentService
from db.sql_alchemy_unit_of_work import SqlAlchemyUnitOfWork, get_db
from fastapi import APIRouter, Depends, Query
from fastapi.exceptions import HTTPException
from pydantic import ValidationError


class DocumentRouter:
    router = APIRouter()

    def __init__(self, document_service: DocumentService):
        self.document_service = document_service
        self._register_routes()

    def _register_routes(self):
        @self.router.get("", status_code=200, response_model=DocumentListResponse)
        async def find_documents_with_filters_pageable(
            filters: Annotated[DocumentFilters, Query()], uow: SqlAlchemyUnitOfWork = Depends(get_db)
        ):
            try:
                return self.document_service.find_documents_with_filters_pageable(session=uow.session, filters=filters)
            except (ValidationError, Exception):
                traceback.print_exc()
                raise HTTPException(status_code=400, detail="bad request")

        @self.router.post("", status_code=201, response_model=DocumentResponse)
        async def create_document(
            new_document_request: NewDocumentRequest, uow: SqlAlchemyUnitOfWork = Depends(get_db)
        ):
            try:
                return self.document_service.create_document(
                    session=uow.session, new_document_request=new_document_request
                )
            except (ValidationError, Exception):
                traceback.print_exc()
                raise HTTPException(status_code=400, detail="bad request")
