from config.logger import logger
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

NOTIFY_FN: str = """
    CREATE OR REPLACE FUNCTION new_ingestion_run_event()
    RETURNS trigger AS $$
    BEGIN
    PERFORM pg_notify('ingestion_run_events', json_build_object(
        'status', NEW.status::text,
        'run_id', NEW.id,
        'workspace_id', NEW.workspace_id
    )::text);
    RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
"""
TRIGGER: str = """
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


async def create_event_channel(conn: AsyncConnection):
    await conn.execute(text(NOTIFY_FN))
    await conn.execute(text(TRIGGER))
    logger.info("event channel ready for new run notify")
