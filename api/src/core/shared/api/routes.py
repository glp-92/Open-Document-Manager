from config.logger import logger
from core.document.infrastructure.pg_events import on_document_uploaded_event
from core.document.infrastructure.repository_impl import DocumentRepositoryImpl
from core.message.infrastructure.pg_events import on_new_ai_chat_message_event
from core.message.infrastructure.repository_impl import MessageRepositoryImpl
from core.run.infrastructure.pg_events import on_ingestion_run_finished_event
from core.run.infrastructure.repository_impl import RunRepositoryImpl
from core.shared.infrastructure.pg_channels import Channels
from db.sql_alchemy_unit_of_work import pg_channel_listener
from fastapi import APIRouter
from fastapi.sse import EventSourceResponse


class SSERouter:
    router = APIRouter()

    def __init__(
        self,
        run_repository_impl: RunRepositoryImpl,
        document_repository_impl: DocumentRepositoryImpl,
        message_repository_impl: MessageRepositoryImpl,
    ):
        self.run_repository_impl = run_repository_impl
        self.document_repository_impl = document_repository_impl
        self.message_repository_impl = message_repository_impl
        self._register_routes()

    def _register_routes(self):
        @self.router.get("/runs", status_code=200, response_class=EventSourceResponse)
        async def on_run_finished_sse():
            logger.info("client connected to /events/runs SSE endpoint")
            async for event in pg_channel_listener(
                Channels.FINISHED_INGESTION_RUN,
                on_ingestion_run_finished_event,
                repository=self.run_repository_impl,
            ):
                yield event

        @self.router.get("/documents", status_code=200, response_class=EventSourceResponse)
        async def on_document_uploaded_sse():
            logger.info("client connected to /events/documents SSE endpoint")
            async for event in pg_channel_listener(
                Channels.FINISHED_UPLOAD_DOCUMENT,
                on_document_uploaded_event,
                repository=self.document_repository_impl,
            ):
                yield event

        @self.router.get("/messages", status_code=200, response_class=EventSourceResponse)
        async def on_chat_message_sse():
            logger.info("client connected to /events/messages SSE endpoint")
            async for event in pg_channel_listener(
                Channels.NEW_AI_CHAT_MESSAGE,
                on_new_ai_chat_message_event,
                repository=self.message_repository_impl,
            ):
                yield event
