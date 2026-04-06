from abc import ABC, abstractmethod

from core.run.api.dto.requests import RunFilters
from core.run.domain.model import Run
from core.run.infrastructure.db_model import DBRun
from sqlalchemy.orm import Session


class RunRepository(ABC):
    @abstractmethod
    def save(self, session: Session, run: Run) -> DBRun:
        pass

    @abstractmethod
    def find_many_filtered_pageable(self, session: Session, filters: RunFilters) -> tuple[list[DBRun], int]:
        pass
