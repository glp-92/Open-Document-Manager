from enum import StrEnum

from core.run.infrastructure.pg_events import (
    FINISHED_INGESTION_RUN_FN,
    FINISHED_INGESTION_RUN_TRIGGER,
    NEW_INGESTION_RUN_FN,
    NEW_INGESTION_RUN_TRIGGER,
)


class Channels(StrEnum):
    NEW_INGESTION_RUN = "new_ingestion_run"
    FINISHED_INGESTION_RUN = "finished_ingestion_run"


CHANNELS_REGISTRY: dict[str, tuple[str, str]] = {
    Channels.NEW_INGESTION_RUN: (NEW_INGESTION_RUN_TRIGGER, NEW_INGESTION_RUN_FN),
    Channels.FINISHED_INGESTION_RUN: (FINISHED_INGESTION_RUN_TRIGGER, FINISHED_INGESTION_RUN_FN),
}
