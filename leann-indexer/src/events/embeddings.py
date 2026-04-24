import os
from typing import Literal

from config.logger import logger
from infrastructure.db_adapter import PostgresDBAdapter, Status
from infrastructure.leann_adapter import LeannAdapter
from infrastructure.s3_adapter import S3Adapter
from pydantic import BaseModel


class EmbeddingsCalculateRequest(BaseModel):
    type: Literal["embeddings", "chat"]
    status: Status
    run_id: str
    workspace_id: str
    urls: list[str]


async def calculate_embeddings(
    payload: dict, s3_adapter: S3Adapter, leann_adapter: LeannAdapter, pg_adapter: PostgresDBAdapter
):
    logger.info(f"received new embedding calc request {payload}")
    embeddings_request: EmbeddingsCalculateRequest = EmbeddingsCalculateRequest(**payload)
    workspace_id: str | None = embeddings_request.workspace_id
    if not workspace_id:
        logger.error("missing workspace_id in embeddings event payload")
        return
    file_urls: list[str] = embeddings_request.urls
    if not file_urls:
        return
    workspace_temp_dir = os.path.join("/temp", workspace_id)
    os.makedirs(workspace_temp_dir, exist_ok=True)
    await s3_adapter.download_files_to_a_directory(
        file_urls=file_urls,
        download_dir=workspace_temp_dir,
    )
    status: Status = leann_adapter.build_index(index_path=workspace_id, docs_path=workspace_temp_dir)
    pg_adapter.change_run_status(run_id=embeddings_request.run_id, status=status)
    logger.info(f"finished processing embedding calc request for workspace {workspace_id} with status {status}")
    return
