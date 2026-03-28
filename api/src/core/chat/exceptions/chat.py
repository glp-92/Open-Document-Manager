from uuid import UUID


class ChatNotFoundError(Exception):
    def __init__(self, chat_id: UUID):
        super().__init__(f"{chat_id}")
