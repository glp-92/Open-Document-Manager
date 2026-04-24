from typing import Literal

from config.logger import logger
from infrastructure.db_adapter import PostgresDBAdapter
from infrastructure.leann_adapter import LeannAdapter
from pydantic import BaseModel


class ChatRequest(BaseModel):
    type: Literal["embeddings", "chat"]
    workspace_id: str
    chat_id: str
    msg: str


async def make_response_on_chat(payload: dict, leann_adapter: LeannAdapter, pg_adapter: PostgresDBAdapter):
    logger.info(f"received chat message {payload}, {pg_adapter}")
    chat_request: ChatRequest = ChatRequest(**payload)
    workspace_id: str | None = chat_request.workspace_id
    msg: str = chat_request.msg
    if not workspace_id:
        logger.error("missing workspace_id in chat event payload")
        return
    _: str = leann_adapter.chat(index_path=workspace_id, msg=msg)
