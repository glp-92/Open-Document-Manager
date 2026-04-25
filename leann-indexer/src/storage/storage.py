from abc import ABC, abstractmethod
from uuid import UUID


class Storage(ABC):
    @abstractmethod
    def get_upload_url(self, bucket: str, filename: str, id: UUID, expires_in: int = 1800) -> str:
        pass

    @abstractmethod
    async def delete_file(self, bucket: str, filename: str):
        pass

    @abstractmethod
    async def download_files_to_a_directory(self, file_urls: list[str], download_dir: str) -> None:
        pass
