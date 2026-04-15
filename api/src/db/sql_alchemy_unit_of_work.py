import datetime
import json
from collections.abc import AsyncGenerator, Callable

from config.config import config
from config.logger import logger
from psycopg import AsyncConnection
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


async def pg_channel_listener(channel_name: str, on_reveive_fn: Callable, repository=None):
    async with await AsyncConnection.connect(engine_url, autocommit=True) as conn:
        await conn.execute(f"LISTEN {channel_name}")
        async for notify in conn.notifies():
            try:
                payload: dict = json.loads(notify.payload)
                async with session_local() as session:
                    data: dict = await on_reveive_fn(session=session, payload=payload, repository=repository)
                    yield {
                        "event": "message",
                        "data": json.dumps(data),
                        "id": str(datetime.datetime.now(datetime.UTC).timestamp()),
                    }
            except Exception as e:
                logger.error(f"error processing notify: {e}")
