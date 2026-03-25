import time

from config.logger import logger
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

MAX_URL_LENGTH = 512
EXCLUDED_PATHS = ["/docs", "/openapi"]


class CustomAccessLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        client_host = request.client.host
        response: Response = await call_next(request)
        user = getattr(request.state, "user", None)
        username = getattr(user, "username", "anonymous")
        full_path: str = str(request.url)
        if any(path in full_path for path in EXCLUDED_PATHS):
            return response
        if len(full_path) > MAX_URL_LENGTH:
            full_path = full_path[:MAX_URL_LENGTH] + "...[truncated]"
        elapsed_time = round(time.time() - start_time, 2)
        log_msg: str = (
            f"{client_host} - {username} - {request.method} {full_path} - {response.status_code} - {elapsed_time}s"
        )
        if response.status_code >= 400:
            logger.error(log_msg)
        else:
            logger.info(log_msg)
        return response


def add_middlewares(app: FastAPI):
    app.add_middleware(CustomAccessLogMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
