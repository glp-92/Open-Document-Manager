import json
import traceback
from collections.abc import Generator

import psycopg
from config.logger import logger
from core.chat.application.service import ChatService
from core.embeddings.application.service import EmbeddingsService
from storage.s3_adapter import S3Adapter
from vector_index.leann_adapter import LeannAdapter


class PGChannelListener:
    def __init__(
        self,
        dsn: str,
        chat_service: ChatService,
        embeddings_service: EmbeddingsService,
        db_unit_of_work: Generator[psycopg.Connection, None, None],
        vector_index_adapter: LeannAdapter,
        storage_adapter: S3Adapter,
    ):
        self.dsn = dsn
        self.chat_service = chat_service
        self.embeddings_service = embeddings_service
        self.db_unit_of_work = db_unit_of_work
        self.vector_index_adapter = vector_index_adapter
        self.storage_adapter = storage_adapter

    async def listen(self):
        logger.info("connecting run events channel...")
        try:
            async with await psycopg.AsyncConnection.connect(self.dsn, autocommit=True) as conn:
                logger.info("connection success! listening new events")
                async with conn.cursor() as cur:
                    await cur.execute("LISTEN ingestion_run_events")
                    await cur.execute("LISTEN new_human_chat_message")
                    async for notify in conn.notifies():
                        logger.info(f"received notify on channel {notify.channel}")
                        payload: dict = json.loads(notify.payload)
                        if notify.channel == "new_human_chat_message":
                            payload.setdefault("type", "chat")
                        match payload.get("type"):
                            case "embeddings":
                                await self.embeddings_service.process(
                                    payload=payload,
                                    db_unit_of_work=self.db_unit_of_work,
                                    storage_adapter=self.storage_adapter,
                                    vector_index_adapter=self.vector_index_adapter,
                                )
                            case "chat":
                                await self.chat_service.process(
                                    payload=payload,
                                    db_unit_of_work=self.db_unit_of_work,
                                    vector_index_adapter=self.vector_index_adapter,
                                )
        except Exception as e:
            traceback.print_exc()
            logger.error(f"worker error: {e}")
