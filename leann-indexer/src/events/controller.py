import json

import psycopg
from config.config import config
from config.logger import logger
from events.chat import make_response_on_chat
from events.embeddings import calculate_embeddings
from infrastructure.db_adapter import PostgresDBAdapter
from infrastructure.leann_adapter import LeannAdapter
from infrastructure.s3_adapter import S3Adapter, get_storage

dsn: str = f"postgresql://{config.db_usr}:{config.db_pwd}@{config.db_host}:{config.db_port}/{config.db_name}"
leann_adapter: LeannAdapter = LeannAdapter()
s3_adapter: S3Adapter = get_storage()
pg_adapter: PostgresDBAdapter = PostgresDBAdapter(dsn=dsn)


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
                            await calculate_embeddings(
                                payload=payload,
                                s3_adapter=s3_adapter,
                                leann_adapter=leann_adapter,
                                pg_adapter=pg_adapter,
                            )
                        case "chat":
                            await make_response_on_chat(
                                payload=payload, leann_adapter=leann_adapter, pg_adapter=pg_adapter
                            )
    except Exception as e:
        logger.error(f"worker error: {e}")
