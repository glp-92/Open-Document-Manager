from typing import Literal

from pydantic import BaseModel


class ChatRequest(BaseModel):
    type: Literal["embeddings", "chat"]
    content: str
    owner: Literal["HUMAN", "AI"]
    message_id: str
    chat_id: str
    workspace_id: str


class Chat(BaseModel):
    model: str
    text: str
    processing_time: str
