import os
from uuid import uuid4

import aioboto3
from botocore.exceptions import ClientError
from fastapi import UploadFile
from app.core.config import settings


class S3CloudConnector:
    def __init__(self):
        self.endpoint = settings.CLOUD_URL
        self.bucket = "test-exercises"
        self.session = aioboto3.Session(
            aws_access_key_id=settings.CLOUD_ACCESS_KEY,
            aws_secret_access_key=settings.CLOUD_SECRET_KEY,
            region_name=settings.CLOUD_REGION,
        )

    async def get_list_objects_on_bucket(self, bucket):
        async with self.session.client("s3", endpoint_url=self.endpoint) as s3:
            try:
                response = await s3.list_objects(Bucket=bucket)
                if "Contents" in response:
                    return [obj["Key"] for obj in response["Contents"]]
                return []
            except ClientError as e:
                print(f"Error: {e}")
                return []

    async def download_file(self, bucket, object_name, local_path):
        async with self.session.client("s3", endpoint_url=self.endpoint) as s3:
            try:
                await s3.download_file(bucket, object_name, local_path)
                return True
            except ClientError as e:
                print(f"Download error: {e}")
                return False

    async def upload_upload_file(self, bucket, file: UploadFile) -> str | None:
        ext = os.path.splitext(file.filename or "")[1]
        key = f"exercises/{uuid4().hex}{ext}"
        async with self.session.client("s3", endpoint_url=self.endpoint) as s3:
            try:
                await s3.upload_fileobj(file.file, bucket, key)
                return f"https://storage.yandexcloud.net/{bucket}/{key}"
            except ClientError as e:
                print(f"Upload error: {e}")
                return None

    async def get_file_url(self, bucket, object_name, expires=3600):
        async with self.session.client("s3", endpoint_url=self.endpoint) as s3:
            try:
                url = await s3.generate_presigned_url(
                    "get_object",
                    Params={"Bucket": bucket, "Key": object_name},
                    ExpiresIn=expires,
                )
                return url
            except ClientError as e:
                print(f"Error: {e}")
                return None


def get_s3_connector() -> S3CloudConnector:
    return S3CloudConnector()
