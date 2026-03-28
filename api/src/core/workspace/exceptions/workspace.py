from uuid import UUID


class WorkspaceNotFoundError(Exception):
    def __init__(self, workspace_id: UUID):
        super().__init__(f"{workspace_id}")
