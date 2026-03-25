from abc import ABC, abstractmethod

from core.workspace.domain.model import Workspace
from core.workspace.infrastructure.db_model import DBWorkspace
from sqlalchemy.orm import Session


class WorkspaceRepository(ABC):
    @abstractmethod
    def save(self, session: Session, workspace: Workspace) -> DBWorkspace:
        pass
