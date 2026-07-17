from typing import BinaryIO, Protocol

from minio import Minio
from minio.error import MinioException, S3Error
from urllib3.exceptions import HTTPError


class StorageError(Exception):
    pass


class DocumentStorage(Protocol):
    def initialize(self) -> None: ...

    def upload_file(
        self,
        storage_path: str,
        data: BinaryIO,
        file_size: int,
        content_type: str,
    ) -> None: ...

    def download_file(self, storage_path: str) -> bytes: ...

    def delete_file(self, storage_path: str) -> None: ...

    def file_exists(self, storage_path: str) -> bool: ...


class MinIOStorage:
    def __init__(self, client: Minio, bucket: str) -> None:
        self._client = client
        self._bucket = bucket
        self._initialized = False

    def initialize(self) -> None:
        if self._initialized:
            return
        try:
            if not self._client.bucket_exists(self._bucket):
                try:
                    self._client.make_bucket(self._bucket)
                except S3Error as exc:
                    if exc.code != "BucketAlreadyOwnedByYou" or not self._client.bucket_exists(
                        self._bucket
                    ):
                        raise
            self._initialized = True
        except (MinioException, HTTPError):
            raise StorageError("Unable to initialize document storage") from None

    def upload_file(
        self,
        storage_path: str,
        data: BinaryIO,
        file_size: int,
        content_type: str,
    ) -> None:
        try:
            self.initialize()
            self._client.put_object(
                self._bucket,
                storage_path,
                data,
                length=file_size,
                content_type=content_type,
            )
        except (MinioException, HTTPError):
            raise StorageError("Unable to upload document") from None

    def download_file(self, storage_path: str) -> bytes:
        try:
            self.initialize()
            response = self._client.get_object(self._bucket, storage_path)
            try:
                return response.read()
            finally:
                response.close()
                response.release_conn()
        except (MinioException, HTTPError):
            raise StorageError("Unable to download document") from None

    def delete_file(self, storage_path: str) -> None:
        try:
            self.initialize()
            self._client.remove_object(self._bucket, storage_path)
        except (MinioException, HTTPError):
            raise StorageError("Unable to delete document") from None

    def file_exists(self, storage_path: str) -> bool:
        try:
            self.initialize()
            self._client.stat_object(self._bucket, storage_path)
            return True
        except S3Error as exc:
            if exc.code in {"NoSuchBucket", "NoSuchKey", "NoSuchObject"}:
                return False
            raise StorageError("Unable to check document") from None
        except (MinioException, HTTPError):
            raise StorageError("Unable to check document") from None
