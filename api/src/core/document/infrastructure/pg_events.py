from core.document.api.dto.requests import UploadFinishedRequest
from core.document.exceptions.document import DocumentNotFoundError
from core.document.infrastructure.db_model import DBDocument
from core.document.infrastructure.repository_impl import DocumentRepositoryImpl
from sqlalchemy.ext.asyncio import AsyncSession

FINISHED_UPLOAD_DOCUMENT_FN: str = """
    CREATE OR REPLACE FUNCTION notify_document_uploaded()
    RETURNS trigger AS $$
    BEGIN
        IF (LOWER(NEW.storage_status) IN ('ready', 'error')) THEN
            PERFORM pg_notify('finished_upload_document', json_build_object(
                'document_id', NEW.id::text,
                'storage_status', LOWER(NEW.storage_status::text)
            )::text);
        END IF;
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
"""
FINISHED_UPLOAD_DOCUMENT_TRIGGER: str = """
    DROP TRIGGER IF EXISTS tr_finished_upload_document_trigger ON documents;
    CREATE TRIGGER tr_finished_upload_document_trigger
    AFTER UPDATE ON documents
    FOR EACH ROW
    WHEN (OLD.storage_status IS DISTINCT FROM NEW.storage_status)
    EXECUTE FUNCTION notify_document_uploaded();
"""


async def on_document_uploaded_event(payload: dict, session: AsyncSession, repository: DocumentRepositoryImpl) -> dict:
    payload: UploadFinishedRequest = UploadFinishedRequest(**payload)
    db_document: DBDocument = await repository.find_by_id(session=session, id=payload.document_id)
    if db_document is None:
        raise DocumentNotFoundError(document_id=payload.document_id)
    return {
        "id": str(db_document.id),
        "workspace_id": str(db_document.workspace_id),
        "storage_status": db_document.storage_status,
    }
