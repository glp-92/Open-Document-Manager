from core.run.api.dto.requests import RunFinishedRequest
from core.run.exceptions.run import RunNotFoundError
from core.run.infrastructure.db_model import DBRun
from core.run.infrastructure.repository_impl import RunRepositoryImpl
from sqlalchemy.ext.asyncio import AsyncSession

NEW_INGESTION_RUN_FN: str = """
    CREATE OR REPLACE FUNCTION new_ingestion_run_event()
    RETURNS trigger AS $$
    DECLARE
        document_urls json;
    BEGIN
        SELECT json_agg(url) INTO document_urls
        FROM documents
        WHERE workspace_id = NEW.workspace_id AND LOWER(storage_status::text) = 'ready';
        PERFORM pg_notify('ingestion_run_events', json_build_object(
            'type', 'embeddings',
            'status', LOWER(NEW.status::text),
            'run_id', NEW.id,
            'workspace_id', NEW.workspace_id,
            'urls', COALESCE(document_urls, '[]'::json)
        )::text);
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
"""
NEW_INGESTION_RUN_TRIGGER: str = """
    DROP TRIGGER IF EXISTS tr_new_run ON runs;
    CREATE TRIGGER tr_new_run
    AFTER INSERT ON runs
    FOR EACH ROW
    WHEN (LOWER(NEW.status::text) = 'pending')
    EXECUTE FUNCTION new_ingestion_run_event();
"""
FINISHED_INGESTION_RUN_FN: str = """
    CREATE OR REPLACE FUNCTION notify_run_finished()
    RETURNS trigger AS $$
    BEGIN
        IF (LOWER(NEW.status::text) IN ('completed', 'error')) THEN
            PERFORM pg_notify('finished_ingestion_run', json_build_object(
                'run_id', NEW.id,
                'status', NEW.status
            )::text);
        END IF;
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
"""
FINISHED_INGESTION_RUN_TRIGGER: str = """
    DROP TRIGGER IF EXISTS tr_finished_run_trigger ON runs;
    CREATE TRIGGER tr_finished_run_trigger
    AFTER UPDATE ON runs
    FOR EACH ROW
    WHEN (OLD.status IS DISTINCT FROM NEW.status)
    EXECUTE FUNCTION notify_run_finished(); -- Nombre corregido para coincidir
"""


async def on_ingestion_run_finished_event(payload: dict, session: AsyncSession, repository: RunRepositoryImpl) -> dict:
    payload: RunFinishedRequest = RunFinishedRequest(**payload)
    db_run: DBRun = await repository.find_by_id(session=session, id=payload.run_id)
    if db_run is None:
        raise RunNotFoundError(run_id=payload.run_id)
    return {"id": str(db_run.id), "workspace_id": str(db_run.workspace_id), "status": db_run.status}
