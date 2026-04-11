import json
import time

import psycopg
from config.config import config
from config.logger import logger

dsn: str = f"postgresql://{config.db_usr}:{config.db_pwd}@{config.db_host}:{config.db_port}/{config.db_name}"


async def pg_channel_listener():
    logger.info("connecting run events channel...")
    try:
        async with await psycopg.AsyncConnection.connect(dsn, autocommit=True) as conn:
            logger.info("connection success! listening new events")
            async with conn.cursor() as cur:
                await cur.execute("listen ingestion_run_events")
                async for notify in conn.notifies():
                    payload: dict = json.loads(notify.payload)
                    logger.info(f"received new event: {json.dumps(payload)}")
                    status: str = payload.get("status", "").lower()
                    if status == "pending":
                        time.sleep(10)
                        logger.info("task completed!")
    except Exception as e:
        logger.error(f"❌ Error crítico en el worker: {e}")
