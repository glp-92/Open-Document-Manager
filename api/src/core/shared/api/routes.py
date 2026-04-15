from config.logger import logger
from core.run.infrastructure.pg_events import on_ingestion_run_finished_event
from core.run.infrastructure.repository_impl import RunRepositoryImpl
from core.shared.infrastructure.pg_channels import Channels
from db.sql_alchemy_unit_of_work import pg_channel_listener
from fastapi import APIRouter
from fastapi.sse import EventSourceResponse


class SSERouter:
    router = APIRouter()

    def __init__(self, run_repository_impl: RunRepositoryImpl):
        self.run_repository_impl = run_repository_impl
        self._register_routes()

    def _register_routes(self):
        @self.router.get("/events", status_code=200, response_class=EventSourceResponse)
        async def on_run_finished_sse():
            logger.info("client connected to /runs/events SSE endpoint")
            async for event in pg_channel_listener(
                Channels.FINISHED_INGESTION_RUN,
                on_ingestion_run_finished_event,
                repository=self.run_repository_impl,
            ):
                yield event
