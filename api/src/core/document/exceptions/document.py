from uuid import UUID


class DocumentNotFoundError(Exception):
    def __init__(self, document_id: UUID):
        super().__init__(f"{document_id}")
