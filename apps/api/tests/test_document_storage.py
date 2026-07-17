from io import BytesIO
from unittest.mock import MagicMock

import pytest
from minio.error import S3Error

from app.core.config import settings
from app.modules.documents import dependencies
from app.modules.documents.dependencies import (
    get_document_storage,
    initialize_document_storage,
)
from app.modules.documents.storage import MinIOStorage


def test_upload_file() -> None:
    client = MagicMock()
    client.bucket_exists.return_value = False
    storage = MinIOStorage(client, "documents")
    data = BytesIO(b"content")

    storage.upload_file("path/manual.pdf", data, 7, "application/pdf")

    client.make_bucket.assert_called_once_with("documents")
    client.put_object.assert_called_once_with(
        "documents",
        "path/manual.pdf",
        data,
        length=7,
        content_type="application/pdf",
    )


def test_download_file() -> None:
    client = MagicMock()
    response = MagicMock()
    response.read.return_value = b"content"
    client.get_object.return_value = response
    storage = MinIOStorage(client, "documents")

    result = storage.download_file("path/manual.pdf")

    assert result == b"content"
    client.get_object.assert_called_once_with("documents", "path/manual.pdf")
    response.close.assert_called_once()
    response.release_conn.assert_called_once()


def test_delete_file() -> None:
    client = MagicMock()
    storage = MinIOStorage(client, "documents")

    storage.delete_file("path/manual.pdf")

    client.remove_object.assert_called_once_with("documents", "path/manual.pdf")


def test_file_exists() -> None:
    client = MagicMock()
    storage = MinIOStorage(client, "documents")

    assert storage.file_exists("path/manual.pdf") is True
    client.stat_object.assert_called_once_with("documents", "path/manual.pdf")


def test_file_exists_returns_false_for_missing_object() -> None:
    client = MagicMock()
    client.stat_object.side_effect = S3Error(
        MagicMock(),
        "NoSuchKey",
        "Object not found",
        "path/missing.pdf",
        "request-id",
        "host-id",
    )
    storage = MinIOStorage(client, "documents")

    assert storage.file_exists("path/missing.pdf") is False


@pytest.mark.parametrize("secure", [False, True])
def test_minio_secure_configuration(monkeypatch, secure: bool) -> None:
    client_factory = MagicMock()
    monkeypatch.setattr(dependencies, "Minio", client_factory)
    monkeypatch.setattr(settings, "minio_secure", secure)

    get_document_storage()

    client_factory.assert_called_once_with(
        settings.minio_endpoint,
        access_key=settings.minio_access_key,
        secret_key=settings.minio_secret_key,
        secure=secure,
    )


def test_initializes_bucket_during_application_startup(monkeypatch) -> None:
    storage = MagicMock()
    monkeypatch.setattr(dependencies, "get_document_storage", lambda: storage)

    initialize_document_storage()

    storage.initialize.assert_called_once()
