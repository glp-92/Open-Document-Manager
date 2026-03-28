from config.config import config
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, declarative_base, sessionmaker

Base: DeclarativeBase = declarative_base()
engine_url: str = (
    f"mysql+mysqlconnector://{config.db_usr}:{config.db_pwd}@{config.db_host}:{config.db_port}/{config.db_name}"
)
engine: Engine = create_engine(url=engine_url, pool_pre_ping=True, pool_recycle=1800, echo=True, echo_pool=True)
session_local: sessionmaker = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class SqlAlchemyUnitOfWork:
    def __init__(self, session: Session):
        self.session = session


def get_db():
    session: Session = session_local()
    try:
        yield SqlAlchemyUnitOfWork(session)
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
