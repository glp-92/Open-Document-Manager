from abc import ABC, abstractmethod


class EmbeddingsService(ABC):
    @abstractmethod
    async def process(self, payload: dict) -> None:
        pass
