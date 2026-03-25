from pydantic import BaseModel


class NewWorkspaceRequest(BaseModel):
    name: str
