from collections.abc import Generator
from contextlib import contextmanager

import psycopg
from config.config import config

dsn: str = f"postgresql://{config.db_usr}:{config.db_pwd}@{config.db_host}:{config.db_port}/{config.db_name}"


@contextmanager
def get_connection(dsn: str) -> Generator[psycopg.Connection, None, None]:
    conn: psycopg.Connection = psycopg.connect(dsn)
    try:
        yield conn
    finally:
        conn.close()
