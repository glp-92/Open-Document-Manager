from contextlib import asynccontextmanager

from config.middlewares import add_middlewares
from core.core import Core
from core.shared.infrastructure.pg_channels import CHANNELS_REGISTRY
from db.sql_alchemy_unit_of_work import Base, engine
from fastapi import FastAPI
from sqlalchemy import text


@asynccontextmanager
async def lifespan(_: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        for trigger, on_trigger_fn in CHANNELS_REGISTRY.values():
            await conn.execute(text(on_trigger_fn))
            await conn.execute(text(trigger))
    yield
    await engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(
        title="Open Document API",
        version="0.1",
        root_path="/api",
        lifespan=lifespan,
    )
    core = Core().app
    app.mount("/v1", core)
    add_middlewares(app=app)
    return app


app: FastAPI = create_app()
