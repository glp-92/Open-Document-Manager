from uuid import UUID


class MessageNotFoundError(Exception):
    def __init__(self, message_id: UUID):
        super().__init__(f"{message_id}")
