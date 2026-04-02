from collections.abc import AsyncGenerator

from config.config import config
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


engine_url: str = (
    f"postgresql+psycopg://{config.db_usr}:{config.db_pwd}@{config.db_host}:{config.db_port}/{config.db_name}"
)

engine: AsyncEngine = create_async_engine(url=engine_url, pool_pre_ping=True, pool_recycle=1800)  # , echo=True)

session_local = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autoflush=False,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with session_local() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
