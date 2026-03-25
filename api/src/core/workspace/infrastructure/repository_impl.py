from core.workspace.domain.model import Workspace
from core.workspace.domain.repository import WorkspaceRepository
from core.workspace.infrastructure.db_model import DBWorkspace
from sqlalchemy.orm import Session


class WorkspaceRepositoryImpl(WorkspaceRepository):
    def __init__(self):
        return

    @staticmethod
    def save(session: Session, workspace: Workspace) -> DBWorkspace:
        db_workspace: DBWorkspace = DBWorkspace.from_domain_object(workspace=workspace)
        session.add(db_workspace)
        session.flush()
        return db_workspace
