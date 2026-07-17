from collections.abc import Generator
from unittest.mock import MagicMock

import pytest

from app.main import app
from app.modules.documents.dependencies import get_document_storage
from app.modules.documents.repository import DocumentRepository
from app.modules.documents.schemas import DocumentStatus


@pytest.fixture()
def storage() -> Generator[MagicMock, None, None]:
    storage_mock = MagicMock()
    app.dependency_overrides[get_document_storage] = lambda: storage_mock
    yield storage_mock
    app.dependency_overrides.pop(get_document_storage, None)


def _create_user(client, email: str, role: str) -> str:
    return client.post(
        "/users", json={"name": role.title(), "email": email, "role": role}
    ).json()["id"]


def _create_document(client, owner_id: str, filename: str = "manual.pdf") -> dict:
    project_id = client.post(
        "/projects", json={"name": filename, "owner_id": owner_id}
    ).json()["id"]
    return client.post(
        f"/projects/{project_id}/documents",
        headers={"X-User-ID": owner_id},
        files={"file": (filename, b"content", "application/pdf")},
    ).json()


def _admin_headers(admin_id: str) -> dict[str, str]:
    return {"X-User-ID": admin_id}


def test_list_all_documents(client, storage) -> None:
    owner_id = _create_user(client, "owner@vena-ia.dev", "member")
    admin_id = _create_user(client, "admin@vena-ia.dev", "admin")
    created = _create_document(client, owner_id)

    response = client.get("/documents", headers=_admin_headers(admin_id))

    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["documents"][0]["id"] == created["id"]


def test_list_ready_documents(client, storage, db_session) -> None:
    owner_id = _create_user(client, "ready-owner@vena-ia.dev", "member")
    admin_id = _create_user(client, "ready-admin@vena-ia.dev", "admin")
    created = _create_document(client, owner_id, "ready.pdf")
    DocumentRepository(db_session).update_status(created["id"], DocumentStatus.READY)

    response = client.get(
        "/documents/status/ready", headers=_admin_headers(admin_id)
    )

    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["documents"][0]["status"] == "READY"


def test_list_processing_documents(client, storage, db_session) -> None:
    owner_id = _create_user(client, "processing-owner@vena-ia.dev", "member")
    admin_id = _create_user(client, "processing-admin@vena-ia.dev", "admin")
    created = _create_document(client, owner_id, "processing.pdf")
    DocumentRepository(db_session).update_status(
        created["id"], DocumentStatus.PROCESSING
    )

    response = client.get(
        "/documents/status/processing", headers=_admin_headers(admin_id)
    )

    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["documents"][0]["status"] == "PROCESSING"


def test_list_failed_documents(client, storage, db_session) -> None:
    owner_id = _create_user(client, "failed-owner@vena-ia.dev", "member")
    admin_id = _create_user(client, "failed-admin@vena-ia.dev", "admin")
    created = _create_document(client, owner_id, "failed.pdf")
    DocumentRepository(db_session).update_status(created["id"], DocumentStatus.FAILED)

    response = client.get(
        "/documents/status/failed", headers=_admin_headers(admin_id)
    )

    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["documents"][0]["status"] == "FAILED"


def test_document_statistics(client, storage, db_session) -> None:
    owner_id = _create_user(client, "stats-owner@vena-ia.dev", "member")
    admin_id = _create_user(client, "stats-admin@vena-ia.dev", "admin")
    documents = [
        _create_document(client, owner_id, f"{status.value.lower()}.pdf")
        for status in DocumentStatus
    ]
    repository = DocumentRepository(db_session)
    for document, status in zip(documents, DocumentStatus, strict=True):
        repository.update_status(document["id"], status)

    response = client.get("/documents/statistics", headers=_admin_headers(admin_id))

    assert response.status_code == 200
    assert response.json() == {
        "total_documents": 4,
        "uploaded": 1,
        "processing": 1,
        "ready": 1,
        "failed": 1,
        "total_storage_bytes": 4 * len(b"content"),
    }


def test_empty_catalog(client, storage) -> None:
    admin_id = _create_user(client, "empty-admin@vena-ia.dev", "admin")
    headers = _admin_headers(admin_id)

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


def test_catalog_requires_administrator(client, storage) -> None:
    member_id = _create_user(client, "catalog-member@vena-ia.dev", "member")

    response = client.get("/documents", headers=_admin_headers(member_id))

    assert response.status_code == 403
    assert response.json() == {"detail": "Administrative access required"}
