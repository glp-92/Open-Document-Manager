import os
import shutil

from config.logger import logger
from core.embeddings.application.embeddings_service import EmbeddingsService
from core.embeddings.domain.model import EmbeddingsRequest
from db.db_adapter import PostgresDBAdapter
from storage.storage import Storage
from vector_index.vector_index import VectorIndex


class EmbeddingsServiceImpl(EmbeddingsService):
    def __init__(self, storage: Storage, vector_index: VectorIndex, db_adapter: PostgresDBAdapter):
        self.storage = storage
        self.vector_index = vector_index
        self.db_adapter = db_adapter

    async def process(self, payload: dict) -> None:
        logger.info(f"received new embedding calc request {payload}")
        request = EmbeddingsRequest(**payload)

        if not request.workspace_id:
            logger.error("missing workspace_id in embeddings event payload")
            return

        if not request.urls:
            return

        workspace_temp_dir = os.path.join("/temp", request.workspace_id)
        os.makedirs(workspace_temp_dir, exist_ok=True)
        try:
            await self.storage.download_files_to_a_directory(
                file_urls=request.urls,
                download_dir=workspace_temp_dir,
            )
            status = self.vector_index.build_index(
                index_path=request.workspace_id,
                docs_path=workspace_temp_dir,
            )
            self.db_adapter.change_run_status(run_id=request.run_id, status=status)
            logger.info(f"finished embedding calc for workspace {request.workspace_id} with status {status}")
        finally:
            shutil.rmtree(workspace_temp_dir, ignore_errors=True)
