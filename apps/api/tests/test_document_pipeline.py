from unittest.mock import MagicMock

import pytest

from app.modules.documents.models import Document
from app.modules.documents.pipeline import (
    DocumentPipeline,
    InvalidDocumentTransitionError,
)
from app.modules.documents.schemas import DocumentStatus


def _document(status: DocumentStatus) -> Document:
    return Document(
        id="document",
        project_id="project",
        filename="manual.pdf",
        content_type="application/pdf",
        file_size=7,
        storage_path="path/manual.pdf",
        status=status.value,
    )


def _pipeline(current: DocumentStatus, target: DocumentStatus) -> tuple[DocumentPipeline, MagicMock]:
    repository = MagicMock()
    repository.get.return_value = _document(current)
    repository.update_status.return_value = _document(target)
    return DocumentPipeline(repository), repository


def test_enqueue_starts_processing() -> None:
    pipeline, repository = _pipeline(DocumentStatus.UPLOADED, DocumentStatus.PROCESSING)

    document = pipeline.enqueue("document")

    assert document.status == DocumentStatus.PROCESSING.value
    repository.update_status.assert_called_once_with(
        "document", DocumentStatus.PROCESSING
    )


def test_start_processing() -> None:
    pipeline, _ = _pipeline(DocumentStatus.UPLOADED, DocumentStatus.PROCESSING)

    document = pipeline.start_processing("document")

    assert document.status == DocumentStatus.PROCESSING.value


def test_finish_processing() -> None:
    pipeline, repository = _pipeline(DocumentStatus.PROCESSING, DocumentStatus.READY)

    document = pipeline.finish_processing("document")

    assert document.status == DocumentStatus.READY.value
    repository.update_status.assert_called_once_with("document", DocumentStatus.READY)


def test_fail_processing() -> None:
    pipeline, repository = _pipeline(DocumentStatus.PROCESSING, DocumentStatus.FAILED)

    document = pipeline.fail_processing("document")

    assert document.status == DocumentStatus.FAILED.value
    repository.update_status.assert_called_once_with("document", DocumentStatus.FAILED)


def test_rejects_invalid_state_transition() -> None:
    pipeline, repository = _pipeline(DocumentStatus.READY, DocumentStatus.PROCESSING)

    with pytest.raises(InvalidDocumentTransitionError):
        pipeline.start_processing("document")

    repository.update_status.assert_not_called()


@pytest.mark.parametrize(
    ("operation", "current"),
    [
        ("start_processing", DocumentStatus.PROCESSING),
        ("start_processing", DocumentStatus.FAILED),
        ("finish_processing", DocumentStatus.UPLOADED),
        ("finish_processing", DocumentStatus.READY),
        ("finish_processing", DocumentStatus.FAILED),
        ("fail_processing", DocumentStatus.UPLOADED),
        ("fail_processing", DocumentStatus.READY),
        ("fail_processing", DocumentStatus.FAILED),
    ],
)
def test_rejects_every_other_invalid_state_transition(
    operation: str, current: DocumentStatus
) -> None:
    pipeline, repository = _pipeline(current, DocumentStatus.PROCESSING)

    with pytest.raises(InvalidDocumentTransitionError):
        getattr(pipeline, operation)("document")

    repository.update_status.assert_not_called()
