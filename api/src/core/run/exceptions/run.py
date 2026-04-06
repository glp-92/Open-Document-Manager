from uuid import UUID


class RunNotFoundError(Exception):
    def __init__(self, run_id: UUID):
        super().__init__(f"{run_id}")
