from uuid import uuid4

import psycopg


class ChatRepositoryImpl:
    def __init__(self):
        pass

    @staticmethod
    def insert_chat_message(cursor: psycopg.Cursor, chat_id: str, content: str, owner: str) -> None:
        cursor.execute(
            "INSERT INTO messages (id, chat_id, content, owner) VALUES (%s, %s, %s, %s)",
            (uuid4(), chat_id, content, owner),
        )
