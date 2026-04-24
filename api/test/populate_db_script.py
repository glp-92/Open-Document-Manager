from random import randint
from uuid import uuid4

import requests
from requests import Response

URL: str = "http://localhost:8080/api/v1"

workspace_payload: dict = {"name": str(uuid4())}

chat_payload: dict = {"workspace_id": None, "name": None}

document_payload: dict = {"chat_id": None, "filename": None, "size": 1, "url": str(uuid4())}

message_payload: dict = {"chat_id": None, "owner": "HUMAN", "content": None}

response: Response = requests.post(url=f"{URL}/workspaces", json=workspace_payload)
workspace_id: str = response.json().get("id")
chat_payload.update({"workspace_id": workspace_id})
for _ in range(randint(1, 2)):
    chat_payload.update({"name": str(uuid4())})
    response: Response = requests.post(url=f"{URL}/chats", json=chat_payload)
    chat_id: str = response.json().get("id")
    message_payload.update({"chat_id": chat_id})
    for _ in range(randint(1, 3)):
        message_payload.update({"content": str(uuid4())})
        response: Response = requests.post(url=f"{URL}/messages", json=message_payload)
    document_payload.update({"chat_id": chat_id})
    for _ in range(randint(1, 3)):
        document_payload.update({"filename": str(uuid4())})
        response: Response = requests.post(url=f"{URL}/documents", json=document_payload)
