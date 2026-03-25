import datetime
from collections.abc import Generator
from contextlib import contextmanager
from uuid import uuid4

from config.config import Config
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, declarative_base, sessionmaker
from sqlalchemy_utils import create_database, database_exists


def gen_utc_timestamp():
    return datetime.datetime.now(datetime.UTC).replace(tzinfo=None)


def gen_uuid():
    return uuid4().bytes


Base: DeclarativeBase = declarative_base()


class SqlAlchemyUnitOfWork:
    def __init__(self, config: Config):
        engine_url: str = (
            f"mysql+mysqlconnector://{config.db_usr}:{config.db_pwd}@{config.db_host}:{config.db_port}/{config.db_name}"
        )
        self.engine = create_engine(engine_url, pool_recycle=1800, pool_pre_ping=True)
        if not database_exists(self.engine.url):
            create_database(self.engine.url)
        self.session_factory = sessionmaker(
            bind=self.engine,
            autoflush=True,
        )

    @contextmanager
    def session(self) -> Generator[Session, None, None]:
        session = self.session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def create_tables(self):
        Base.metadata.create_all(self.engine)
