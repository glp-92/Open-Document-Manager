from typing import Literal

from config.logger import logger
from infrastructure.db_adapter import PostgresDBAdapter
from infrastructure.leann_adapter import LeannAdapter
from pydantic import BaseModel


class ChatRequest(BaseModel):
    type: Literal["embeddings", "chat"]
    content: str
    owner: Literal["HUMAN", "AI"]
    message_id: str
    chat_id: str
    workspace_id: str


async def make_response_on_chat(payload: dict, leann_adapter: LeannAdapter, pg_adapter: PostgresDBAdapter):
    logger.info(f"received chat message {payload}")
    chat_request: ChatRequest = ChatRequest(**payload)
    workspace_id: str | None = chat_request.workspace_id
    content: str = chat_request.content
    if not workspace_id:
        logger.error("missing workspace_id in chat event payload")
        return
    response: str = leann_adapter.chat(index_path=workspace_id, msg=content)
    logger.info(f"full chat response: {response}")
    pg_adapter.insert_chat_message(chat_id=chat_request.chat_id, content=response, owner="AI")
    logger.info(f"finished processing chat request for workspace {workspace_id}")
    return
