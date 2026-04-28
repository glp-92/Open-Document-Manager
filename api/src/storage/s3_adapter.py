import asyncio
import os
from concurrent.futures import ThreadPoolExecutor
from uuid import UUID

import boto3
from botocore.client import ClientError, Config
from config.config import config
from config.logger import logger
from mypy_boto3_s3 import S3Client


class S3Adapter:
    def __init__(self):
        internal_endpoint_url = f"http://{config.storage_host}:{config.storage_port}"
        public_endpoint_url = self._normalize_endpoint_url(
            config.storage_public_url,
            fallback=internal_endpoint_url,
        )

        self.client: S3Client = boto3.client(
            service_name="s3",
            aws_access_key_id=config.storage_usr,
            aws_secret_access_key=config.storage_pwd,
            endpoint_url=internal_endpoint_url,
            config=Config(signature_version="s3v4"),
        )
        self.presign_client: S3Client = (
            self.client
            if public_endpoint_url == internal_endpoint_url
            else boto3.client(
                service_name="s3",
                aws_access_key_id=config.storage_usr,
                aws_secret_access_key=config.storage_pwd,
                endpoint_url=public_endpoint_url,
                config=Config(signature_version="s3v4"),
            )
        )
        try:
            self.client.create_bucket(Bucket=config.storage_bucket)
        except self.client.exceptions.BucketAlreadyExists:
            logger.info(f"bucket {config.storage_bucket} already exists")
        self._executor = ThreadPoolExecutor(max_workers=10)

    @staticmethod
    def _normalize_endpoint_url(endpoint: str | None, fallback: str) -> str:
        if endpoint is None or endpoint.strip() == "":
            return fallback
        endpoint = endpoint.strip().rstrip("/")
        if endpoint.startswith("http://") or endpoint.startswith("https://"):
            return endpoint
        return f"http://{endpoint}"

    def get_upload_url(self, bucket: str, filename: str, id: UUID, expires_in: int = 1800) -> str:
        try:
            return self.presign_client.generate_presigned_url(
                "put_object",
                Params={"Bucket": bucket, "Key": f"{id}/{os.path.basename(filename)}"},
                ExpiresIn=expires_in,
            )
        except ClientError as e:
            logger.error(f"presigned url retrieve error: {e}")
            raise

    async def delete_file(self, bucket: str, filename: str):
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(self._executor, self.client.delete_object, bucket, filename)


_storage_adapter = S3Adapter()


def get_storage() -> S3Adapter:
    return _storage_adapter
