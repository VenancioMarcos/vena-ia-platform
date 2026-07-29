from collections.abc import Generator
from unittest.mock import MagicMock

import pytest

from app.main import app
from app.modules.documents.dependencies import get_document_storage
from app.modules.documents.repository import DocumentRepository
from app.modules.documents.schemas import DocumentStatus

PDF_BYTES = b"%PDF-1.7\ncontent\n%%EOF"


@pytest.fixture()
def storage() -> Generator[MagicMock, None, None]:
    storage_mock = MagicMock()
    app.dependency_overrides[get_document_storage] = lambda: storage_mock
    yield storage_mock
    app.dependency_overrides.pop(get_document_storage, None)


def _create_document(client, owner, filename: str = "manual.pdf") -> dict:
    project_id = client.post(
        "/projects",
        headers=owner.headers,
        json={"name": filename},
    ).json()["id"]
    return client.post(
        f"/projects/{project_id}/documents",
        headers=owner.headers,
        files={"file": (filename, PDF_BYTES, "application/pdf")},
    ).json()


def test_list_all_documents(client, storage, make_account) -> None:
    owner = make_account("owner@vena-ia.dev")
    admin = make_account("admin@vena-ia.dev", role="admin")
    created = _create_document(client, owner)

    response = client.get("/documents", headers=admin.headers)

    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["documents"][0]["id"] == created["id"]


def test_list_ready_documents(client, storage, db_session, make_account) -> None:
    owner = make_account("ready-owner@vena-ia.dev")
    admin = make_account("ready-admin@vena-ia.dev", role="admin")
    created = _create_document(client, owner, "ready.pdf")
    DocumentRepository(db_session).update_status(created["id"], DocumentStatus.READY)

    response = client.get(
        "/documents/status/ready", headers=admin.headers
    )

    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["documents"][0]["status"] == "READY"


def test_list_processing_documents(client, storage, db_session, make_account) -> None:
    owner = make_account("processing-owner@vena-ia.dev")
    admin = make_account("processing-admin@vena-ia.dev", role="admin")
    created = _create_document(client, owner, "processing.pdf")
    DocumentRepository(db_session).update_status(
        created["id"], DocumentStatus.PROCESSING
    )

    response = client.get(
        "/documents/status/processing", headers=admin.headers
    )

    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["documents"][0]["status"] == "PROCESSING"


def test_list_failed_documents(client, storage, db_session, make_account) -> None:
    owner = make_account("failed-owner@vena-ia.dev")
    admin = make_account("failed-admin@vena-ia.dev", role="admin")
    created = _create_document(client, owner, "failed.pdf")
    DocumentRepository(db_session).update_status(created["id"], DocumentStatus.FAILED)

    response = client.get(
        "/documents/status/failed", headers=admin.headers
    )

    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["documents"][0]["status"] == "FAILED"


def test_document_statistics(client, storage, db_session, make_account) -> None:
    owner = make_account("stats-owner@vena-ia.dev")
    admin = make_account("stats-admin@vena-ia.dev", role="admin")
    documents = [
        _create_document(client, owner, f"{status.value.lower()}.pdf")
        for status in DocumentStatus
    ]
    repository = DocumentRepository(db_session)
    for document, status in zip(documents, DocumentStatus, strict=True):
        repository.update_status(document["id"], status)

    response = client.get("/documents/statistics", headers=admin.headers)

    assert response.status_code == 200
    assert response.json() == {
        "total_documents": 4,
        "uploaded": 1,
        "processing": 1,
        "ready": 1,
        "failed": 1,
        "total_storage_bytes": 4 * len(PDF_BYTES),
    }


def test_empty_catalog(client, storage, make_account) -> None:
    admin = make_account("empty-admin@vena-ia.dev", role="admin")
    headers = admin.headers

    lists = [
        client.get("/documents", headers=headers),
        client.get("/documents/status/ready", headers=headers),
        client.get("/documents/status/processing", headers=headers),
        client.get("/documents/status/failed", headers=headers),
    ]
    statistics = client.get("/documents/statistics", headers=headers)

    assert all(response.status_code == 200 for response in lists)
    assert all(response.json() == {"documents": [], "total": 0} for response in lists)
    assert statistics.json() == {
        "total_documents": 0,
        "uploaded": 0,
        "processing": 0,
        "ready": 0,
        "failed": 0,
        "total_storage_bytes": 0,
    }


def test_catalog_requires_administrator(client, storage, make_account) -> None:
    member = make_account("catalog-member@vena-ia.dev")

    response = client.get("/documents", headers=member.headers)

    assert response.status_code == 403
    assert response.json() == {"detail": "Administrative access required"}
