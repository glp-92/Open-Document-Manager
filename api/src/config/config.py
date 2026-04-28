import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent.parent.parent / ".env")


@dataclass
class Config:
    db_host: str
    db_port: str
    db_usr: str
    db_pwd: str
    db_name: str
    storage_host: str
    storage_port: str
    storage_public_url: str | None
    storage_usr: str
    storage_pwd: str
    storage_bucket: str
    storage_presigned_url_expiration: int
    ollama_url: str


config = Config(
    db_host=os.environ.get("DB_HOST", "localhost"),
    db_port=os.environ.get("DB_PORT", "5432"),
    db_usr=os.environ.get("DB_USR", "testuser"),
    db_pwd=os.environ.get("DB_PWD", "testuser"),
    db_name=os.environ.get("DB_NAME", "testdb"),
    storage_host=os.environ.get("STORAGE_HOST", "localhost"),
    storage_port=os.environ.get("STORAGE_PORT", "8883"),
    storage_public_url=os.environ.get("STORAGE_PUBLIC_URL"),
    storage_usr=os.environ.get("STORAGE_USR", "testuser"),
    storage_pwd=os.environ.get("STORAGE_PWD", "testpwd"),
    storage_bucket=os.environ.get("STORAGE_BUCKET", "testbucket"),
    storage_presigned_url_expiration=int(os.environ.get("STORAGE_PRESIGNED_URL_EXPIRATION", 1800)),
    ollama_url=os.environ.get("OLLAMA_URL", "testuser"),
)
