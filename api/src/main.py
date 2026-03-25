from contextlib import asynccontextmanager

from config.config import config
from config.middlewares import add_middlewares
from core.core import Core
from db.sql_alchemy_unit_of_work import SqlAlchemyUnitOfWork
from fastapi import FastAPI

db_connector = SqlAlchemyUnitOfWork(config=config)


@asynccontextmanager
async def lifespan(_: FastAPI):
    db_connector.create_tables()
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="Open Document API",
        version="0.1",
        root_path="/api",
        lifespan=lifespan,
    )
    core = Core(sql_session_factory=db_connector.session).app
    app.mount("/v1", core)
    add_middlewares(app=app)
    return app


app: FastAPI = create_app()
