from abc import ABC, abstractmethod


class TranslationService(ABC):
    @abstractmethod
    def detect_language(self, text: str) -> str:
        pass

    @abstractmethod
    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        pass
