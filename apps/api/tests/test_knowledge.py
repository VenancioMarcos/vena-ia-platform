from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.modules.documents.contracts import (
    EmbeddingUpdateResult,
    KnowledgeAnswer,
    KnowledgeMatch,
)
from app.modules.documents.dependencies import get_knowledge_service
from app.modules.documents.knowledge import KnowledgeIndexError, KnowledgeService
from app.modules.documents.models import Document, DocumentChunk
from packages.ai.core import ChatResult, EmbeddingsResult


def _document(status: str = "READY") -> Document:
    return Document(
        id="document",
        project_id="project",
        filename="manual.pdf",
        content_type="application/pdf",
        file_size=100,
        storage_path="documents/manual.pdf",
        status=status,
    )


def _chunk(index: int = 0) -> DocumentChunk:
    return DocumentChunk(
        id=f"chunk-{index}",
        document_id="document",
        page_number=2,
        chunk_index=index,
        start_offset=0,
        end_offset=12,
        character_count=12,
        content="cutting data",
        created_at=datetime.now(timezone.utc),
    )


def _service(dimensions: int = 3) -> tuple[KnowledgeService, MagicMock, MagicMock]:
    documents = MagicMock()
    documents.get.return_value = _document()
    authorization = MagicMock()
    repository = MagicMock()
    ai = MagicMock()
    service = KnowledgeService(
        document_service=documents,
        authorization=authorization,
        chunk_repository=repository,
        ai_service=ai,
        provider="test",
        embedding_model="embed-test",
        chat_model="chat-test",
        embedding_dimensions=dimensions,
    )
    return service, repository, ai


def test_indexes_all_document_chunks() -> None:
    service, repository, ai = _service()
    chunks = [_chunk(0), _chunk(1)]
    repository.list_for_document.return_value = chunks
    repository.update_embeddings.return_value = 2
    ai.embeddings.return_value = EmbeddingsResult(
        provider="test",
        model="embed-test",
        embeddings=[[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]],
    )

    result = service.index_document("document")

    assert result.embedded_chunks == 2
    repository.update_embeddings.assert_called_once_with(
        chunks,
        [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]],
        "embed-test",
    )


def test_rejects_invalid_embedding_dimensions() -> None:
    service, repository, ai = _service()
    repository.list_for_document.return_value = [_chunk()]
    ai.embeddings.return_value = EmbeddingsResult(
        provider="test",
        model="embed-test",
        embeddings=[[1.0, 0.0]],
    )

    with pytest.raises(KnowledgeIndexError, match="dimension"):
        service.index_document("document")


def test_grounded_answer_uses_citations_and_untrusted_context() -> None:
    service, repository, ai = _service()
    match = KnowledgeMatch(chunk=_chunk(), score=0.91)
    ai.embeddings.return_value = EmbeddingsResult(
        provider="test",
        model="embed-test",
        embeddings=[[1.0, 0.0, 0.0]],
    )
    repository.semantic_search.return_value = [match]
    ai.chat.return_value = ChatResult(
        provider="test",
        model="chat-test",
        content="Use 120 m/min.",
    )

    result = service.answer("project", "What speed?", 5)

    assert result.matches == [match]
    request = ai.chat.call_args.args[1]
    assert "untrusted data" in request.messages[0].content
    assert "document=document page=2 chunk=0" in request.messages[1].content


def test_search_route_serializes_traceability(client: TestClient) -> None:
    service = MagicMock()
    service.search.return_value = [KnowledgeMatch(chunk=_chunk(), score=0.91)]
    app.dependency_overrides[get_knowledge_service] = lambda: service
    try:
        response = client.post(
            "/projects/project/knowledge/search",
            json={"query": "speed", "limit": 3},
        )
    finally:
        app.dependency_overrides.pop(get_knowledge_service, None)

    assert response.status_code == 200
    assert response.json()["matches"][0] == {
        "document_id": "document",
        "page_number": 2,
        "chunk_index": 0,
        "content": "cutting data",
        "score": 0.91,
    }


def test_embedding_route_returns_index_result(client: TestClient) -> None:
    service = MagicMock()
    service.index_document.return_value = EmbeddingUpdateResult(
        document_id="document",
        embedded_chunks=4,
        model="embed-test",
    )
    app.dependency_overrides[get_knowledge_service] = lambda: service
    try:
        response = client.post("/documents/document/embeddings")
    finally:
        app.dependency_overrides.pop(get_knowledge_service, None)

    assert response.status_code == 200
    assert response.json() == {
        "document_id": "document",
        "embedded_chunks": 4,
        "model": "embed-test",
    }


def test_ask_route_returns_grounded_answer(client: TestClient) -> None:
    service = MagicMock()
    match = KnowledgeMatch(chunk=_chunk(), score=0.91)
    service.answer.return_value = KnowledgeAnswer(
        answer="Use 120 m/min.",
        provider="test",
        model="chat-test",
        matches=[match],
    )
    app.dependency_overrides[get_knowledge_service] = lambda: service
    try:
        response = client.post(
            "/projects/project/knowledge/ask",
            json={"question": "What speed?", "limit": 3},
        )
    finally:
        app.dependency_overrides.pop(get_knowledge_service, None)

    assert response.status_code == 200
    assert response.json()["answer"] == "Use 120 m/min."
    assert response.json()["matches"][0]["page_number"] == 2
