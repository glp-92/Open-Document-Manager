import asyncio
import os

from channels.pg_channel_listener import PGChannelListener
from config.config import config
from config.logger import logger
from core.chat.infrastructure.chat_service_impl import ChatServiceImpl
from core.chat.infrastructure.translation_service_impl import TranslationServiceImpl
from core.embeddings.infrastructure.embeddings_service_impl import EmbeddingsServiceImpl
from db.db_adapter import PostgresDBAdapter
from storage.s3_adapter import get_storage
from vector_index.leann_adapter import LeannAdapter

os.makedirs("/temp", exist_ok=True)

dsn: str = f"postgresql://{config.db_usr}:{config.db_pwd}@{config.db_host}:{config.db_port}/{config.db_name}"
db_adapter = PostgresDBAdapter(dsn=dsn)
leann_adapter = LeannAdapter()

chat_service = ChatServiceImpl(
    vector_index=leann_adapter,
    translation_service=TranslationServiceImpl(),
    db_adapter=db_adapter,
)
embeddings_service = EmbeddingsServiceImpl(
    storage=get_storage(),
    vector_index=leann_adapter,
    db_adapter=db_adapter,
)

listener = PGChannelListener(dsn=dsn, chat_service=chat_service, embeddings_service=embeddings_service)

if __name__ == "__main__":
    try:
        asyncio.run(listener.listen())
    except KeyboardInterrupt:
        logger.info("\nworker shut down")
