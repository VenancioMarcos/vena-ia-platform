from collections.abc import Generator
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app
from app.modules.documents.dependencies import (
    get_document_service,
    get_document_storage,
)
from app.modules.documents.storage import StorageError


@pytest.fixture()
def storage() -> Generator[MagicMock, None, None]:
    storage_mock = MagicMock()
    app.dependency_overrides[get_document_storage] = lambda: storage_mock
    yield storage_mock
    app.dependency_overrides.pop(get_document_storage, None)


def _create_project(client, email: str = "documents@vena-ia.dev") -> tuple[str, str]:
    user = client.post(
        "/users",
        json={"name": "Document Owner", "email": email, "role": "member"},
    ).json()
    project = client.post(
        "/projects", json={"name": "Knowledge Base", "owner_id": user["id"]}
    ).json()
    return project["id"], user["id"]


def _headers(user_id: str) -> dict[str, str]:
    return {"X-User-ID": user_id}


def _upload_document(client, project_id: str, user_id: str, filename: str = "machine-manual.pdf"):
    return client.post(
        f"/projects/{project_id}/documents",
        headers=_headers(user_id),
        files={"file": (filename, b"manual contents", "application/pdf")},
    )


def test_create_document(client, storage) -> None:
    project_id, user_id = _create_project(client)

    response = _upload_document(client, project_id, user_id)

    assert response.status_code == 201
    assert response.json()["project_id"] == project_id
    assert response.json()["filename"] == "machine-manual.pdf"
    assert response.json()["content_type"] == "application/pdf"
    assert response.json()["file_size"] == len(b"manual contents")
    assert response.json()["storage_path"].startswith(f"projects/{project_id}/documents/")
    assert response.json()["status"] == "UPLOADED"
    storage.upload_file.assert_called_once()


def test_list_documents_by_project(client, storage) -> None:
    project_id, user_id = _create_project(client)
    _upload_document(client, project_id, user_id)

    response = client.get(
        f"/projects/{project_id}/documents", headers=_headers(user_id)
    )

    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["documents"][0]["filename"] == "machine-manual.pdf"


def test_get_document(client, storage) -> None:
    project_id, user_id = _create_project(client)
    created = _upload_document(client, project_id, user_id).json()

    response = client.get(f"/documents/{created['id']}", headers=_headers(user_id))

    assert response.status_code == 200
    assert response.json() == created


def test_delete_document_is_idempotent(client, storage) -> None:
    project_id, user_id = _create_project(client)
    created = _upload_document(client, project_id, user_id).json()

    first = client.delete(f"/documents/{created['id']}", headers=_headers(user_id))
    second = client.delete(f"/documents/{created['id']}", headers=_headers(user_id))

    assert first.status_code == 204
    assert second.status_code == 204
    storage.delete_file.assert_called_once_with(created["storage_path"])


def test_sanitizes_path_traversal_and_malicious_filename(client, storage) -> None:
    project_id, user_id = _create_project(client)

    response = _upload_document(client, project_id, user_id, "..\\..\\evil<script>.pdf")

    assert response.status_code == 201
    assert response.json()["filename"] == "evil_script_.pdf"
    assert ".." not in response.json()["storage_path"]
    assert "\\" not in response.json()["storage_path"]


def test_rejects_file_above_configured_limit(client, storage, monkeypatch) -> None:
    project_id, user_id = _create_project(client)
    monkeypatch.setattr(settings, "document_max_file_size", 4)

    response = _upload_document(client, project_id, user_id)

    assert response.status_code == 413
    storage.upload_file.assert_not_called()


def test_rejects_invalid_content_type(client, storage) -> None:
    project_id, user_id = _create_project(client)

    response = client.post(
        f"/projects/{project_id}/documents",
        headers=_headers(user_id),
        files={"file": ("manual.pdf", b"content", "invalid-content-type")},
    )

    assert response.status_code == 400
    storage.upload_file.assert_not_called()


def test_requires_authentication(client, storage) -> None:
    project_id, _ = _create_project(client)

    response = client.get(f"/projects/{project_id}/documents")

    assert response.status_code == 401


def test_denies_access_to_another_owner_documents(client, storage) -> None:
    project_id, owner_id = _create_project(client)
    _, other_user_id = _create_project(client, "other@vena-ia.dev")
    _upload_document(client, project_id, owner_id)

    response = client.get(
        f"/projects/{project_id}/documents", headers=_headers(other_user_id)
    )

    assert response.status_code == 403


def test_returns_not_found_for_missing_document(client, storage) -> None:
    _, user_id = _create_project(client)

    response = client.get("/documents/missing", headers=_headers(user_id))

    assert response.status_code == 404


def test_storage_unavailable_does_not_persist_or_expose_credentials(client, storage) -> None:
    project_id, user_id = _create_project(client)
    storage.upload_file.side_effect = StorageError("MINIO_SECRET_KEY=supersecret")

    uploaded = _upload_document(client, project_id, user_id)
    listed = client.get(
        f"/projects/{project_id}/documents", headers=_headers(user_id)
    )

    assert uploaded.status_code == 503
    assert uploaded.json() == {"detail": "Document storage unavailable"}
    assert "supersecret" not in uploaded.text
    assert listed.json()["total"] == 0


def test_storage_delete_failure_preserves_database_record(client, storage) -> None:
    project_id, user_id = _create_project(client)
    created = _upload_document(client, project_id, user_id).json()
    storage.delete_file.side_effect = StorageError("unavailable")

    deleted = client.delete(f"/documents/{created['id']}", headers=_headers(user_id))
    fetched = client.get(f"/documents/{created['id']}", headers=_headers(user_id))

    assert deleted.status_code == 503
    assert fetched.status_code == 200


def test_count_documents_by_project(client, storage) -> None:
    project_id, user_id = _create_project(client)
    _upload_document(client, project_id, user_id, "first.pdf")
    _upload_document(client, project_id, user_id, "second.pdf")

    response = client.get(
        f"/projects/{project_id}/documents/count", headers=_headers(user_id)
    )

    assert response.status_code == 200
    assert response.json() == {"project_id": project_id, "count": 2}


def test_list_documents_returns_not_found_for_missing_project(client, storage) -> None:
    _, user_id = _create_project(client)

    response = client.get(
        "/projects/missing/documents", headers=_headers(user_id)
    )

    assert response.status_code == 404


def test_remove_document_returns_not_found_for_missing_document(client, storage) -> None:
    project_id, user_id = _create_project(client)

    response = client.delete(
        f"/projects/{project_id}/documents/missing", headers=_headers(user_id)
    )

    assert response.status_code == 404
    storage.delete_file.assert_not_called()


def test_remove_document_rejects_document_from_another_project(client, storage) -> None:
    project_id, user_id = _create_project(client)
    other_project = client.post(
        "/projects", json={"name": "Other Project", "owner_id": user_id}
    ).json()
    created = _upload_document(client, project_id, user_id).json()

    response = client.delete(
        f"/projects/{other_project['id']}/documents/{created['id']}",
        headers=_headers(user_id),
    )

    assert response.status_code == 409
    storage.delete_file.assert_not_called()


def test_remove_document_deletes_database_record_and_storage(client, storage) -> None:
    project_id, user_id = _create_project(client)
    created = _upload_document(client, project_id, user_id).json()

    removed = client.delete(
        f"/projects/{project_id}/documents/{created['id']}",
        headers=_headers(user_id),
    )
    fetched = client.get(f"/documents/{created['id']}", headers=_headers(user_id))

    assert removed.status_code == 204
    assert fetched.status_code == 404
    storage.delete_file.assert_called_once_with(created["storage_path"])


def test_process_document_changes_status_to_processing(client, storage) -> None:
    project_id, user_id = _create_project(client)
    created = _upload_document(client, project_id, user_id).json()

    processed = client.post(
        f"/documents/{created['id']}/process", headers=_headers(user_id)
    )
    fetched = client.get(f"/documents/{created['id']}", headers=_headers(user_id))

    assert processed.status_code == 200
    assert processed.json()["status"] == "PROCESSING"
    assert fetched.json()["status"] == "PROCESSING"


def test_upload_without_file_returns_unprocessable_entity(client, storage) -> None:
    project_id, user_id = _create_project(client)

    response = client.post(
        f"/projects/{project_id}/documents",
        headers=_headers(user_id),
    )

    assert response.status_code == 422
    storage.upload_file.assert_not_called()


def test_process_document_rejects_repeated_transition(client, storage) -> None:
    project_id, user_id = _create_project(client)
    created = _upload_document(client, project_id, user_id).json()

    first = client.post(
        f"/documents/{created['id']}/process", headers=_headers(user_id)
    )
    second = client.post(
        f"/documents/{created['id']}/process", headers=_headers(user_id)
    )

    assert first.status_code == 200
    assert second.status_code == 409


def test_unexpected_internal_error_returns_500_without_details() -> None:
    service = MagicMock()
    service.list_all_documents.side_effect = RuntimeError("internal-sensitive-detail")
    app.dependency_overrides[get_document_service] = lambda: service
    internal_client = TestClient(app, raise_server_exceptions=False)

    try:
        response = internal_client.get("/documents")
    finally:
        internal_client.close()
        app.dependency_overrides.pop(get_document_service, None)

    assert response.status_code == 500
    assert "internal-sensitive-detail" not in response.text
