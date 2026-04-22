import asyncio
import os

from config.logger import logger
from infrastructure.events import pg_channel_listener

os.makedirs("/temp", exist_ok=True)

if __name__ == "__main__":
    try:
        asyncio.run(pg_channel_listener())
    except KeyboardInterrupt:
        logger.info("\nworker shut down")
