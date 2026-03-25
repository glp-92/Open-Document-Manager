import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent.parent.parent / ".env")


@dataclass
class Config:
    db_usr: str
    db_pwd: str
    db_host: str
    db_port: str
    db_name: str
    ollama_url: str


config = Config(
    db_usr=os.environ.get("DB_USR", "testuser"),
    db_pwd=os.environ.get("DB_PWD", "testuser"),
    db_host=os.environ.get("DB_HOST", "localhost"),
    db_port=os.environ.get("DB_PORT", "5432"),
    db_name=os.environ.get("DB_NAME", "testdb"),
    ollama_url=os.environ.get("OLLAMA_URL", "testuser"),
)
