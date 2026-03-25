import logging
import sys
from typing import Any

from loguru import logger


class EndpointFilter(logging.Filter):
    def __init__(
        self,
        path: str,
        *args: Any,
        **kwargs: Any,
    ):
        super().__init__(*args, **kwargs)
        self._path = path

    def filter(self, record: logging.LogRecord) -> bool:
        return record.getMessage().find(self._path) == -1


uvicorn_logger = logging.getLogger("uvicorn.access")
uvicorn_logger.addFilter(EndpointFilter(path="/"))

LoggerFormat = (
    "<green>{time:YY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level: <8}</level> | {name} | "
    "<level>{message}</level> | {extra}"
)

logger.remove()

logger.add(
    sys.stdout,
    level="INFO",
    format=LoggerFormat,
    serialize="False",
    enqueue=True,
    diagnose=False,
)
