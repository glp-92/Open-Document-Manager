from abc import ABC, abstractmethod


class ChatService(ABC):
    @abstractmethod
    async def process(self, payload: dict) -> None:
        pass
