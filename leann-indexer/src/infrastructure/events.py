import json
import os

import psycopg
from config.config import config
from config.logger import logger
from infrastructure.leann_adapter import LeannAdapter
from infrastructure.s3_adapter import S3Adapter, get_storage

dsn: str = f"postgresql://{config.db_usr}:{config.db_pwd}@{config.db_host}:{config.db_port}/{config.db_name}"
leann_adapter: LeannAdapter = LeannAdapter()
s3_adapter: S3Adapter = get_storage()


async def pg_channel_listener():
    logger.info("connecting run events channel...")
    try:
        async with await psycopg.AsyncConnection.connect(dsn, autocommit=True) as conn:
            logger.info("connection success! listening new events")
            async with conn.cursor() as cur:
                await cur.execute("listen ingestion_run_events")
                async for notify in conn.notifies():
                    payload: dict = json.loads(notify.payload)
                    match payload.get("type"):
                        case "embeddings":
                            logger.info(f"received new embedding calc request {payload}")
                            workspace_id: str | None = payload.get("workspace_id")
                            if not workspace_id:
                                logger.error("missing workspace_id in embeddings event payload")
                                continue
                            file_urls: list[str] = payload.get("urls")
                            if not file_urls:
                                continue
                            workspace_temp_dir = os.path.join("/temp", workspace_id)
                            os.makedirs(workspace_temp_dir, exist_ok=True)
                            await s3_adapter.download_files_to_a_directory(
                                file_urls=file_urls,
                                download_dir=workspace_temp_dir,
                            )
                            leann_adapter.build_index(index_path=workspace_id, docs_path=workspace_temp_dir)
                        case "chat":
                            workspace_id: str | None = payload.get("workspace_id")
                            logger.info(f"received chat message from workspace {workspace_id}")
                            msg: str = payload.get("msg")
                            if not workspace_id:
                                logger.error("missing workspace_id in chat event payload")
                                continue
                            _: str = leann_adapter.chat(index_path=workspace_id, msg=msg)

    except Exception as e:
        logger.error(f"worker error: {e}")
