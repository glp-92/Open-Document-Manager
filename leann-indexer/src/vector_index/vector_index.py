from abc import ABC, abstractmethod

from core.shared.runs import RunStatus


class VectorIndex(ABC):
    @abstractmethod
    def build_index(self, index_path: str, docs_path: str) -> RunStatus:
        pass

    @abstractmethod
    def chat_with_index(self, index_path: str, msg: str) -> str:
        pass
