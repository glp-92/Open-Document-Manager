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


conn_string: str = f"{config.db_usr}:{config.db_pwd}@{config.db_host}:{config.db_port}/{config.db_name}"
engine_url: str = f"postgresql+psycopg://{conn_string}"
pg_dsn: str = f"postgresql://{conn_string}"

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


async def pg_channel_listener(channel_name: str, on_receive_fn: Callable, repository=None):
    conn = await AsyncConnection.connect(pg_dsn, autocommit=True)
    async with conn:
        await conn.execute(f"LISTEN {channel_name}")
        async for notify in conn.notifies():
            try:
                payload = json.loads(notify.payload)
                async with session_local() as session:
                    data = await on_receive_fn(session=session, payload=payload, repository=repository)
                    yield {
                        "event": "message",
                        "data": json.dumps(data),
                        "id": str(datetime.datetime.now(datetime.UTC).timestamp()),
                    }
            except Exception as e:
                logger.error(f"error processing notify: {e}")
                continue
