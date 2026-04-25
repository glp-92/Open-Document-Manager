from typing import Literal

from core.shared.runs import RunStatus
from pydantic import BaseModel


class EmbeddingsRequest(BaseModel):
    type: Literal["embeddings", "chat"]
    status: RunStatus
    run_id: str
    workspace_id: str
    urls: list[str]
