import asyncio

from config.logger import logger
from infrastructure.postgres_channels_listeners import pg_channel_listener

if __name__ == "__main__":
    try:
        asyncio.run(pg_channel_listener())
    except KeyboardInterrupt:
        logger.info("\nworker shut down")
