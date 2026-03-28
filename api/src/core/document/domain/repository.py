from abc import ABC, abstractmethod

from core.document.api.dto.requests import DocumentFilters
from core.document.domain.model import Document
from core.document.infrastructure.db_model import DBDocument
from sqlalchemy.orm import Session


class DocumentRepository(ABC):
    @abstractmethod
    def save(self, session: Session, document: Document) -> DBDocument:
        pass

    @abstractmethod
    def find_many_filtered_pageable(self, session: Session, filters: DocumentFilters) -> tuple[list[DBDocument], int]:
        pass
