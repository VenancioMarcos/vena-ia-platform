from unittest.mock import MagicMock

import pytest

from app.modules.documents.chunking import CharacterTextChunker
from app.modules.documents.contracts import ExtractedPage
from app.modules.documents.extraction import PdfExtractionError
from app.modules.documents.models import Document
from app.modules.documents.processing import (
    DocumentContentUnavailableError,
    DocumentProcessingService,
)
from app.modules.documents.storage import StorageError
from app.core.metrics import InMemoryMetricCollector


def _document(status: str) -> Document:
    return Document(
        id="document",
        project_id="project",
        filename="manual.pdf",
        content_type="application/pdf",
        file_size=100,
        storage_path="documents/manual.pdf",
        status=status,
    )


def _processor() -> tuple[DocumentProcessingService, MagicMock, MagicMock, MagicMock]:
    document_service = MagicMock()
    document_service.get.return_value = _document("UPLOADED")
    document_service.finish_processing.return_value = _document("READY")
    repository = MagicMock()
    repository.replace_for_document.side_effect = lambda _document_id, chunks: chunks
    storage = MagicMock()
    storage.download_file.return_value = b"%PDF-1.7\nfixture"
    extractor = MagicMock()
    extractor.extract_pages.return_value = [
        ExtractedPage(page_number=1, text="alpha beta gamma"),
        ExtractedPage(page_number=2, text="delta"),
    ]
    processor = DocumentProcessingService(
        document_service=document_service,
        chunk_repository=repository,
        storage=storage,
        extractor=extractor,
        chunker=CharacterTextChunker(chunk_size=10, overlap=2),
    )
    return processor, document_service, repository, storage


def test_processes_pdf_and_persists_traceable_chunks() -> None:
    processor, document_service, repository, storage = _processor()

    result = processor.process("document")

    assert result.document.status == "READY"
    assert result.chunk_count == 3
    document_service.start_processing.assert_called_once_with("document")
    document_service.finish_processing.assert_called_once_with("document")
    storage.download_file.assert_called_once_with("documents/manual.pdf")
    chunks = repository.replace_for_document.call_args.args[1]
    assert [(chunk.page_number, chunk.chunk_index) for chunk in chunks] == [
        (1, 0),
        (1, 1),
        (2, 2),
    ]
    assert all(chunk.document_id == "document" for chunk in chunks)


def test_marks_document_failed_when_extraction_fails() -> None:
    processor, document_service, _repository, _storage = _processor()
    processor._extractor.extract_pages.side_effect = PdfExtractionError("invalid")

    with pytest.raises(PdfExtractionError, match="invalid"):
        processor.process("document")

    document_service.fail_processing.assert_called_once_with("document")
    document_service.finish_processing.assert_not_called()


def test_maps_storage_failure_and_marks_document_failed() -> None:
    processor, document_service, _repository, storage = _processor()
    storage.download_file.side_effect = StorageError("secret internal detail")

    with pytest.raises(
        DocumentContentUnavailableError,
        match="Document storage unavailable",
    ):
        processor.process("document")

    document_service.fail_processing.assert_called_once_with("document")


def test_chunk_query_checks_document_access() -> None:
    processor, document_service, repository, _storage = _processor()
    repository.list_for_document.return_value = []

    assert processor.list_chunks("document", page_number=2) == []

    document_service.get.assert_called_once_with("document")
    repository.list_for_document.assert_called_once_with("document", 2)


def test_processing_retry_and_started_job_are_aggregated() -> None:
    processor, document_service, _repository, _storage = _processor()
    collector = InMemoryMetricCollector()
    processor._metric_collector = collector
    document_service.get.return_value = _document("FAILED")

    processor.process("document")

    snapshot = collector.snapshot()
    labels = {
        item["name"]: item["labels"]
        for item in snapshot["series"]  # type: ignore[index]
    }
    assert labels["processing_jobs_total"] == {
        "operation": "document.processing",
        "outcome": "started",
    }
    assert labels["retry_attempts_total"] == {"operation": "document.processing"}
