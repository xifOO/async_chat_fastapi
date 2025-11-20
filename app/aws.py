import os
from contextlib import AsyncExitStack
from typing import Optional

from aiobotocore.session import AioSession
from botocore.exceptions import ClientError

from app.config import settings
from app.exceptions import AWSDownloadError, AWSError, AWSUploadError


class AWSManager:
    def __init__(self) -> None:
        self._session = AioSession()
        self._exit_stack = AsyncExitStack()

    async def _create_s3_client(self):
        try:
            client = await self._exit_stack.enter_async_context(
                self._session.create_client(
                    "s3",
                    endpoint_url=settings.aws.endpoint_url,
                    region_name=settings.aws.region,
                    aws_access_key_id=settings.aws.access_key_id,
                    aws_secret_access_key=settings.aws.secret_access_key,
                )
            )
            return client
        except ClientError as e:
            raise AWSError(f"Failed to connect to S3: {e}") from e

    async def _generate_presigned_url(
        self,
        operation: str,
        *,
        Params: dict,
        ExpiresIn: int,
        object_name: Optional[str] = None,
    ):
        try:
            if object_name is None:
                object_name = os.path.basename(Params["Key"])

            client = await self._create_s3_client()

            url = await client.generate_presigned_url(
                operation, Params=Params, ExpiresIn=ExpiresIn
            )  # type: ignore

            return url
        except ClientError as e:
            raise AWSError(f"Failed to generate presigned URL: {e}") from e
        finally:
            await self._exit_stack.aclose()

    async def _retrieve_file_etag(
        self, file_name: str, *, object_name: Optional[str] = None
    ) -> Optional[str]:
        if object_name is None:
            object_name = os.path.basename(file_name)

        client = await self._create_s3_client()
        try:
            resp = await client.head_object(Bucket=settings.aws.bucket, Key=file_name)  # type: ignore
            etag = resp["ETag"].strip('"')
            return etag
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "404":
                return None
            raise AWSError(f"Failed to retrieve file ETag: {e}") from e
        finally:
            await self._exit_stack.aclose()

    async def upload_file(
        self,
        file_name: str,
        file_type: str,
        file_etag: str,
        *,
        object_name: Optional[str] = None,
    ) -> Optional[str]:
        try:
            etag = await self._retrieve_file_etag(file_name, object_name=object_name)
            if etag != file_etag:
                url = await self._generate_presigned_url(
                    "put_object",
                    Params={
                        "Bucket": settings.aws.bucket,
                        "Key": object_name or file_name,
                        "ContentType": file_type,
                    },
                    ExpiresIn=3600,
                )
                return url

            return None
        except AWSError as e:
            raise AWSUploadError(str(e)) from e

    async def download_file(
        self, file_name: str, file_type: str, *, object_name: Optional[str] = None
    ) -> Optional[str]:
        try:
            url = await self._generate_presigned_url(
                "get_object",
                Params={
                    "Bucket": settings.aws.bucket,
                    "Key": object_name or file_name,
                    "ResponseContentType": file_type,
                },
                ExpiresIn=3600,
            )
            return url
        except AWSError as e:
            raise AWSDownloadError(str(e)) from e
