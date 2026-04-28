import psycopg
from core.shared.schemas.runs import RunStatus


class EmbeddingsRepositoryImpl:
    def __init__(self):
        pass

    @staticmethod
    def change_run_status(cursor: psycopg.Cursor, run_id: str, status: RunStatus) -> None:
        cursor.execute("UPDATE runs SET status = %s WHERE id = %s", (status, run_id))
