import asyncio
import os
from concurrent.futures import ThreadPoolExecutor
from uuid import UUID

import boto3
from botocore.client import ClientError, Config
from config.config import config
from config.logger import logger
from mypy_boto3_s3 import S3Client
from storage.storage import Storage


class S3Adapter(Storage):
    def __init__(self):
        self.client: S3Client = boto3.client(
            service_name="s3",
            aws_access_key_id=config.storage_usr,
            aws_secret_access_key=config.storage_pwd,
            endpoint_url=f"http://{config.storage_host}:{config.storage_port}",
            config=Config(signature_version="s3v4"),
        )
        try:
            self.client.create_bucket(Bucket=config.storage_bucket)
        except self.client.exceptions.BucketAlreadyExists:
            logger.info(f"bucket {config.storage_bucket} already exists")
        self._executor = ThreadPoolExecutor(max_workers=10)

    def get_upload_url(self, bucket: str, filename: str, id: UUID, expires_in: int = 1800) -> str:
        try:
            return self.client.generate_presigned_url(
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

    def _parse_s3_url(self, url: str) -> tuple[str, str]:
        if not url.startswith("/buckets/"):
            raise ValueError(f"invalid s3 url: {url}")
        bucket, file_id, filename = url.split("/")[2:5]
        key = f"{file_id}/{filename}"
        return bucket, key

    async def download_files_to_a_directory(self, file_urls: list[str], download_dir: str):
        loop = asyncio.get_running_loop()
        tasks = []
        for url in file_urls:
            bucket, key = self._parse_s3_url(url)
            filename = os.path.basename(key)
            task = loop.run_in_executor(
                self._executor, self.client.download_file, bucket, key, os.path.join(download_dir, filename)
            )
            tasks.append(task)
        await asyncio.gather(*tasks)


_storage_adapter = S3Adapter()


def get_storage() -> S3Adapter:
    return _storage_adapter
