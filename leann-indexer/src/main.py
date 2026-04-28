import asyncio
import functools
import os

from config.logger import logger
from core.chat.application.service import ChatService
from core.chat.infrastructure.repository_impl import ChatRepositoryImpl
from core.embeddings.application.service import EmbeddingsService
from core.embeddings.infrastructure.repository_impl import EmbeddingsRepositoryImpl
from core.shared.infrastructure.pg_channels import PGChannelListener
from db.pg_unit_of_work import dsn, get_connection
from storage.s3_adapter import S3Adapter
from vector_index.leann_adapter import LeannAdapter

os.makedirs("/temp", exist_ok=True)

db_unit_of_work = functools.partial(get_connection, dsn)
storage_adapter: S3Adapter = S3Adapter()
vector_index_adapter: LeannAdapter = LeannAdapter()
chat_service = ChatService(
    chat_repository_impl=ChatRepositoryImpl(),
)
embeddings_service = EmbeddingsService(
    embeddings_repository_impl=EmbeddingsRepositoryImpl(),
)
listener = PGChannelListener(
    dsn=dsn,
    chat_service=chat_service,
    embeddings_service=embeddings_service,
    db_unit_of_work=db_unit_of_work,
    vector_index_adapter=vector_index_adapter,
    storage_adapter=storage_adapter,
)

if __name__ == "__main__":
    try:
        asyncio.run(listener.listen())
    except KeyboardInterrupt:
        logger.info("\nworker shut down")
