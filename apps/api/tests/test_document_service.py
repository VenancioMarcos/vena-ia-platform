from io import BytesIO
from unittest.mock import MagicMock

import pytest
from fastapi import UploadFile
from starlette.datastructures import Headers

from app.modules.documents.models import Document
from app.modules.documents.repository import DocumentRepository
from app.modules.documents.service import (
    DocumentService,
    DocumentStorageError,
    InvalidDocumentError,
)
from app.modules.documents.storage import StorageError
from app.modules.projects.models import Project


def _upload_file() -> UploadFile:
    return UploadFile(
        file=BytesIO(b"content"),
        filename="manual.pdf",
        headers=Headers({"content-type": "application/pdf"}),
    )


def _service(repository: MagicMock, storage: MagicMock, db: MagicMock) -> DocumentService:
    db.get.return_value = Project(id="project", name="Project", owner_id="owner")
    return DocumentService(repository, storage, db, 1024, "owner", MagicMock())


def test_removes_uploaded_object_when_database_create_fails() -> None:
    repository = MagicMock()
    repository.create.side_effect = RuntimeError("database unavailable")
    storage = MagicMock()
    service = _service(repository, storage, MagicMock())

    with pytest.raises(RuntimeError, match="database unavailable"):
        service.create("project", _upload_file())

    storage.upload_file.assert_called_once()
    storage.delete_file.assert_called_once()


def test_does_not_write_database_when_upload_fails() -> None:
    repository = MagicMock()
    storage = MagicMock()
    storage.upload_file.side_effect = StorageError("unavailable")
    service = _service(repository, storage, MagicMock())

    with pytest.raises(DocumentStorageError, match="Document storage unavailable"):
        service.create("project", _upload_file())

    repository.create.assert_not_called()


def test_does_not_delete_database_record_when_storage_delete_fails() -> None:
    repository = MagicMock()
    repository.get.return_value = Document(
        id="document",
        project_id="project",
        filename="manual.pdf",
        content_type="application/pdf",
        file_size=7,
        storage_path="path/manual.pdf",
        status="UPLOADED",
    )
    storage = MagicMock()
    storage.delete_file.side_effect = StorageError("unavailable")
    service = _service(repository, storage, MagicMock())

    with pytest.raises(DocumentStorageError, match="Document storage unavailable"):
        service.delete("document")

    repository.delete.assert_not_called()


def test_delete_missing_document_is_idempotent() -> None:
    repository = MagicMock()
    repository.get.return_value = None
    storage = MagicMock()
    service = _service(repository, storage, MagicMock())

    service.delete("missing")

    storage.delete_file.assert_not_called()
    repository.delete.assert_not_called()


def test_rejects_missing_content_type() -> None:
    repository = MagicMock()
    storage = MagicMock()
    service = _service(repository, storage, MagicMock())
    file = UploadFile(file=BytesIO(b"content"), filename="manual.pdf")

    with pytest.raises(InvalidDocumentError, match="Valid content type is required"):
        service.create("project", file)

    storage.upload_file.assert_not_called()
    repository.create.assert_not_called()


def test_repository_rolls_back_when_database_commit_fails() -> None:
    db = MagicMock()
    db.commit.side_effect = RuntimeError("database unavailable")
    repository = DocumentRepository(db)
    document = Document(
        id="document",
        project_id="project",
        filename="manual.pdf",
        content_type="application/pdf",
        file_size=7,
        storage_path="path/manual.pdf",
        status="UPLOADED",
    )

    with pytest.raises(RuntimeError, match="database unavailable"):
        repository.create(document)

    db.rollback.assert_called_once()
