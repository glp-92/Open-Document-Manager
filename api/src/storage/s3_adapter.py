import boto3
from botocore.client import Config
from config.config import config
from mypy_boto3_s3 import S3Client


class S3UnitOfWork:
    def __init__(self):
        self.client: S3Client = boto3.client(
            service_name="s3",
            aws_access_key_id=config.storage_usr,
            aws_secret_access_key=config.storage_pwd,
            endpoint_url=f"http://{config.storage_host}:{config.storage_port}",
            config=Config(signature_version="s3v4"),
        )

    def get_upload_url(
        self,
        bucket: str,
        filename: str,
    ) -> str:
        return self.client.generate_presigned_url(
            "put_object", Params={"Bucket": bucket, "Key": filename}, ExpiresIn=1800
        )


def get_storage() -> S3UnitOfWork:
    return S3UnitOfWork()
