from abc import ABC, abstractmethod

from core.shared.runs import RunStatus


class DB(ABC):
    @abstractmethod
    def change_run_status(self, run_id: str, status: RunStatus) -> None:
        pass

    @abstractmethod
    def insert_chat_message(self, chat_id: str, content: str, owner: str) -> None:
        pass
