from config.logger import logger
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

NEW_INGESTION_RUN_FN: str = """
    CREATE OR REPLACE FUNCTION new_ingestion_run_event()
    RETURNS trigger AS $$
    DECLARE
        document_urls json;
    BEGIN
        SELECT json_agg(url) INTO document_urls
        FROM documents
        WHERE workspace_id = NEW.workspace_id;
        PERFORM pg_notify('ingestion_run_events', json_build_object(
            'type', 'embeddings',
            'status', NEW.status::text,
            'run_id', NEW.id,
            'workspace_id', NEW.workspace_id,
            'urls', COALESCE(document_urls, '[]'::json) -- Si no hay, envía array vacío
        )::text);
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
"""
NEW_INGESTION_RUN_TRIGGER: str = """
    DO $$
    BEGIN
        DROP TRIGGER IF EXISTS tr_new_run ON runs;
        CREATE TRIGGER tr_new_run
        AFTER INSERT OR UPDATE ON runs
        FOR EACH ROW
        WHEN (LOWER(NEW.status::text) = 'pending')
        EXECUTE FUNCTION new_ingestion_run_event();
    END $$;
"""
FINISHED_INGESTION_RUN_FN: str = """
    CREATE OR REPLACE FUNCTION notify_run_finished()
    RETURNS trigger AS $$
    BEGIN
        IF (NEW.status::text IN ('completed', 'error')) THEN
            PERFORM pg_notify('ingestion run finished', json_build_object(
                'run_id', NEW.id,
                'workspace_id', NEW.workspace_id,
                'status', NEW.status::text,
                'message', 'ingest finished'
            )::text);
        END IF;
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
"""
FINISHED_INGESTION_RUN_TRIGGER: str = """
    O $$
    BEGIN
        DROP TRIGGER IF EXISTS tr_finished_run ON runs;
        CREATE TRIGGER tr_finished_run
        AFTER UPDATE ON runs
        FOR EACH ROW
        WHEN (OLD.status IS DISTINCT FROM NEW.status)
        EXECUTE FUNCTION notify_run_finished();
    END $$;
"""


async def create_event_channel(conn: AsyncConnection):
    await conn.execute(text(NEW_INGESTION_RUN_FN))
    await conn.execute(text(NEW_INGESTION_RUN_TRIGGER))
    logger.info("event channel ready for new run notify")
    # await conn.execute(text(FINISHED_INGESTION_RUN_FN))
    # await conn.execute(text(FINISHED_INGESTION_RUN_TRIGGER))
    logger.info("event channel ready run finish notify")
