from contextlib import contextmanager
from enum import StrEnum

import psycopg


class Status(StrEnum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    ERROR = "ERROR"
    DELETED = "DELETED"


class PostgresDBAdapter:
    def __init__(self, dsn: str):
        self.dsn = dsn

    @contextmanager
    def get_connection(self):
        conn = psycopg.connect(self.dsn)
        try:
            yield conn
        finally:
            conn.close()

    def change_run_status(self, run_id: str, status: Status) -> None:
        with self.get_connection() as conn, conn.cursor() as cur:
            cur.execute("UPDATE runs SET status = %s WHERE id = %s", (status, run_id))
            conn.commit()
