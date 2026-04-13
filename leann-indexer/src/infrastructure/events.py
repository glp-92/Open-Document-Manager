import json

import psycopg
from config.config import config
from config.logger import logger
from infrastructure.leann_adapter import LeannAdapter

dsn: str = f"postgresql://{config.db_usr}:{config.db_pwd}@{config.db_host}:{config.db_port}/{config.db_name}"
leann_adapter: LeannAdapter = LeannAdapter()


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
                            file_urls: list[str] = payload.get("urls")
                            if not file_urls:
                                continue
                            workspace_id: str = payload.get("workspace")
                            leann_adapter.build_index(index_path=workspace_id, docs_path="./temp")
                        case "chat":
                            logger.info(f"received chat message from workspace {payload.get('workspace')}")
                            msg: str = payload.get("msg")
                            _: str = leann_adapter.chat(index_path=workspace_id, msg=msg)

    except Exception as e:
        logger.error(f"worker error: {e}")
