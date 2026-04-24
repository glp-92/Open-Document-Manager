from core.message.api.dto.requests import NewMessageFromIARequest
from core.message.exceptions.workspace import MessageNotFoundError
from core.message.infrastructure.db_model import DBMessage
from core.message.infrastructure.repository_impl import MessageRepositoryImpl
from sqlalchemy.ext.asyncio import AsyncSession

NEW_CHAT_MESSAGE_FN: str = """
    CREATE OR REPLACE FUNCTION notify_new_chat_message()
    RETURNS trigger AS $$
    BEGIN
        IF NEW.owner::text = 'HUMAN' THEN
            PERFORM pg_notify('new_chat_message', json_build_object(
                'type', 'chat',
                'content', NEW.content,
                'owner', NEW.owner,
                'message_id', NEW.id,
                'chat_id', NEW.chat_id,
            )::text);
        END IF;
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
"""
NEW_CHAT_MESSAGE_TRIGGER: str = """
    DROP TRIGGER IF EXISTS tr_new_chat_message_trigger ON messages;
    CREATE TRIGGER tr_new_chat_message_trigger
    AFTER INSERT ON messages
    FOR EACH ROW
    WHEN (NEW.owner::text = 'HUMAN')
    EXECUTE FUNCTION notify_new_chat_message();
"""


async def on_new_chat_message_event(payload: dict, session: AsyncSession, repository: MessageRepositoryImpl) -> dict:
    payload: NewMessageFromIARequest = NewMessageFromIARequest(**payload)
    db_message: DBMessage = await repository.find_by_id(session=session, id=payload.message_id)
    if db_message is None:
        raise MessageNotFoundError(message_id=payload.message_id)
    return {
        "id": str(db_message.id),
        "chat_id": str(db_message.chat_id),
        "content": db_message.content,
        "owner": db_message.owner,
        "created_at": db_message.created_at,
        "updated_at": db_message.updated_at,
    }
