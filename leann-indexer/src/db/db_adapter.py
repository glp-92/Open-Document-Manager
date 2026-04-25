from contextlib import contextmanager
from uuid import uuid4

import psycopg
from core.shared.runs import RunStatus
from db.db import DB


class PostgresDBAdapter(DB):
    def __init__(self, dsn: str):
        self.dsn = dsn

    @contextmanager
    def _get_connection(self):
        conn = psycopg.connect(self.dsn)
        try:
            yield conn
        finally:
            conn.close()

    def change_run_status(self, run_id: str, status: RunStatus) -> None:
        with self._get_connection() as conn, conn.cursor() as cur:
            cur.execute("UPDATE runs SET status = %s WHERE id = %s", (status, run_id))
            conn.commit()

    def insert_chat_message(self, chat_id: str, content: str, owner: str) -> None:
        with self._get_connection() as conn, conn.cursor() as cur:
            cur.execute(
                "INSERT INTO messages (id, chat_id, content, owner) VALUES (%s, %s, %s, %s)",
                (uuid4(), chat_id, content, owner),
            )
            conn.commit()
