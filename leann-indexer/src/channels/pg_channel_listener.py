import json
import traceback

import psycopg
from config.logger import logger
from core.chat.application.chat_service import ChatService
from core.embeddings.application.embeddings_service import EmbeddingsService


class PGChannelListener:
    def __init__(self, dsn: str, chat_service: ChatService, embeddings_service: EmbeddingsService):
        self.dsn = dsn
        self.chat_service = chat_service
        self.embeddings_service = embeddings_service

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
                                await self.embeddings_service.process(payload=payload)
                            case "chat":
                                await self.chat_service.process(payload=payload)
        except Exception as e:
            traceback.print_exc()
            logger.error(f"worker error: {e}")
