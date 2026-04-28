import sys

from loguru import logger

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
    serialize=False,
    enqueue=True,
    diagnose=False,
)
