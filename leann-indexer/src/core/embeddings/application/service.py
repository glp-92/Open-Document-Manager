import os
import shutil

import psycopg
from config.logger import logger
from core.embeddings.infrastructure.repository_impl import EmbeddingsRepositoryImpl
from core.embeddings.schemas.requests import EmbeddingsRequest
from storage.s3_adapter import S3Adapter
from vector_index.leann_adapter import LeannAdapter


class EmbeddingsService:
    def __init__(self, embeddings_repository_impl: EmbeddingsRepositoryImpl):
        self.embeddings_repository_impl = embeddings_repository_impl

    async def process(
        self,
        payload: dict,
        db_unit_of_work: psycopg.Connection,
        storage_adapter: S3Adapter,
        vector_index_adapter: LeannAdapter,
    ) -> None:
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
            await storage_adapter.download_files_to_a_directory(
                file_urls=request.urls,
                download_dir=workspace_temp_dir,
            )
            status = vector_index_adapter.build_index(
                index_path=request.workspace_id,
                docs_path=workspace_temp_dir,
            )
            with db_unit_of_work() as conn, conn.cursor() as cur:
                self.embeddings_repository_impl.change_run_status(cursor=cur, run_id=request.run_id, status=status)
                conn.commit()
            logger.info(f"finished embedding calc for workspace {request.workspace_id} with status {status}")
        finally:
            shutil.rmtree(workspace_temp_dir, ignore_errors=True)
