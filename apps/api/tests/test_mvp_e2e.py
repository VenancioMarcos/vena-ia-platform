from collections.abc import Generator
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.modules.documents.contracts import (
    EmbeddingUpdateResult,
    ExtractedPage,
    KnowledgeAnswer,
    KnowledgeMatch,
)
from app.modules.documents.dependencies import (
    get_document_storage,
    get_knowledge_service,
    get_pdf_text_extractor,
)
from app.modules.documents.models import DocumentChunk
from conftest import TEST_PASSWORD

PDF_BYTES = b"%PDF-1.7\nMVP integration evidence\n%%EOF"


class DeterministicKnowledge:
    def __init__(self) -> None:
        self.document_id = ""

    def index_document(self, document_id: str) -> EmbeddingUpdateResult:
        self.document_id = document_id
        return EmbeddingUpdateResult(
            document_id=document_id,
            embedded_chunks=1,
            model="deterministic-test-embedding",
        )

    def answer(self, project_id: str, question: str, limit: int) -> KnowledgeAnswer:
        assert project_id
        assert question
        assert limit >= 1
        chunk = DocumentChunk(
            id="deterministic-chunk",
            document_id=self.document_id,
            page_number=1,
            chunk_index=0,
            start_offset=0,
            end_offset=43,
            character_count=43,
            content="Maintenance requires a documented inspection.",
        )
        return KnowledgeAnswer(
            answer="The document requires a documented inspection.",
            provider="deterministic-test",
            model="deterministic-test-chat",
            matches=[KnowledgeMatch(chunk=chunk, score=1.0)],
        )


@pytest.fixture()
def mvp_dependencies() -> Generator[None, None, None]:
    storage = MagicMock()
    storage.download_file.return_value = PDF_BYTES
    extractor = MagicMock()
    extractor.extract_pages.return_value = [
        ExtractedPage(
            page_number=1,
            text="Maintenance requires a documented inspection.",
        )
    ]
    knowledge = DeterministicKnowledge()
    app.dependency_overrides[get_document_storage] = lambda: storage
    app.dependency_overrides[get_pdf_text_extractor] = lambda: extractor
    app.dependency_overrides[get_knowledge_service] = lambda: knowledge
    yield
    app.dependency_overrides.pop(get_document_storage, None)
    app.dependency_overrides.pop(get_pdf_text_extractor, None)
    app.dependency_overrides.pop(get_knowledge_service, None)


def _account(client: TestClient, email: str) -> dict[str, str]:
    registered = client.post(
        "/auth/register",
        json={"name": "MVP User", "email": email, "password": TEST_PASSWORD},
    )
    assert registered.status_code == 201, registered.text
    logged_in = client.post(
        "/auth/login",
        json={"email": email, "password": TEST_PASSWORD},
    )
    assert logged_in.status_code == 200, logged_in.text
    client.cookies.clear()
    return {"Authorization": f"Bearer {logged_in.json()['access_token']}"}


def test_mvp_end_to_end_and_cross_user_authorization(
    client: TestClient,
    mvp_dependencies: None,
) -> None:
    owner_headers = _account(client, "mvp-owner@vena-ia.dev")
    project = client.post(
        "/projects",
        headers=owner_headers,
        json={"name": "Integrated MVP"},
    )
    assert project.status_code == 201
    project_id = project.json()["id"]

    uploaded = client.post(
        f"/projects/{project_id}/documents",
        headers=owner_headers,
        files={"file": ("evidence.pdf", PDF_BYTES, "application/pdf")},
    )
    assert uploaded.status_code == 201, uploaded.text
    document_id = uploaded.json()["id"]

    processed = client.post(
        f"/documents/{document_id}/processing",
        headers=owner_headers,
    )
    assert processed.status_code == 200, processed.text
    assert processed.json()["chunk_count"] == 1

    indexed = client.post(
        f"/documents/{document_id}/embeddings",
        headers=owner_headers,
    )
    assert indexed.status_code == 200
    assert indexed.json()["model"] == "deterministic-test-embedding"

    answered = client.post(
        f"/chat/{project_id}/ask",
        headers=owner_headers,
        json={"question": "What inspection is required?"},
    )
    assert answered.status_code == 200, answered.text
    assistant = answered.json()["assistant_message"]
    assert assistant["role"] == "assistant"
    assert assistant["status"] == "COMPLETED"
    assert assistant["evidence"][0]["document_id"] == document_id
    assert assistant["evidence"][0]["page_number"] == 1

    history = client.get(
        f"/chat/{project_id}/messages",
        headers=owner_headers,
    )
    assert history.status_code == 200
    assert [message["role"] for message in history.json()] == ["user", "assistant"]

    report = client.post(
        "/research/reports",
        headers=owner_headers,
        json={
            "project_id": project_id,
            "report_type": "TECHNICAL_SYNTHESIS",
            "title": "MVP technical report",
            "objective": "Record grounded evidence",
            "document_ids": [document_id],
            "synthesis": assistant["content"],
            "evidence": assistant["evidence"],
            "limitations": ["Requires human review."],
        },
    )
    assert report.status_code == 201, report.text
    report_id = report.json()["id"]
    reopened = client.get(
        f"/research/reports/{report_id}",
        headers=owner_headers,
    )
    assert reopened.status_code == 200
    assert reopened.json()["status"] == "DRAFT_REQUIRES_AUTHOR_REVIEW"

    outsider_headers = _account(client, "mvp-outsider@vena-ia.dev")
    for method, path in [
        ("GET", f"/projects/{project_id}"),
        ("GET", f"/projects/{project_id}/documents"),
        ("GET", f"/documents/{document_id}/chunks"),
        ("GET", f"/chat/{project_id}/messages"),
        ("GET", f"/research/reports/{report_id}"),
    ]:
        response = client.request(method, path, headers=outsider_headers)
        assert response.status_code == 404, (path, response.text)

    logged_out = client.post("/auth/logout", headers=owner_headers)
    assert logged_out.status_code == 204
    client.cookies.clear()
    assert client.get(f"/projects/{project_id}").status_code == 401
