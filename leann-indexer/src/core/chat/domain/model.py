from pydantic import BaseModel


class Chat(BaseModel):
    model: str
    text: str
    processing_time: str
