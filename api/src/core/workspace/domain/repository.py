from abc import ABC, abstractmethod

from core.workspace.api.dto.requests import WorkspaceFilters
from core.workspace.domain.model import Workspace
from core.workspace.infrastructure.db_model import DBWorkspace
from sqlalchemy.orm import Session


class WorkspaceRepository(ABC):
    @abstractmethod
    def save(self, session: Session, workspace: Workspace) -> DBWorkspace:
        pass

    @abstractmethod
    def find_many_filtered_pageable(self, session: Session, filters: WorkspaceFilters) -> tuple[list[DBWorkspace], int]:
        pass
