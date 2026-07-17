from app.modules.documents.models import Document
from app.modules.documents.repository import DocumentRepository
from app.modules.documents.schemas import DocumentStatus


class PipelineDocumentNotFoundError(Exception):
    pass


class InvalidDocumentTransitionError(Exception):
    pass


class DocumentPipeline:
    """Controls document states without processing document content."""

    def __init__(self, repository: DocumentRepository) -> None:
        self._repository = repository

    def enqueue(self, document_id: str) -> Document:
        return self.start_processing(document_id)

    def start_processing(self, document_id: str) -> Document:
        return self._transition(
            document_id,
            expected=DocumentStatus.UPLOADED,
            target=DocumentStatus.PROCESSING,
        )

    def finish_processing(self, document_id: str) -> Document:
        return self._transition(
            document_id,
            expected=DocumentStatus.PROCESSING,
            target=DocumentStatus.READY,
        )

    def fail_processing(self, document_id: str) -> Document:
        return self._transition(
            document_id,
            expected=DocumentStatus.PROCESSING,
            target=DocumentStatus.FAILED,
        )

    def _transition(
        self,
        document_id: str,
        expected: DocumentStatus,
        target: DocumentStatus,
    ) -> Document:
        document = self._repository.get(document_id)
        if document is None:
            raise PipelineDocumentNotFoundError("Document not found")

        try:
            current = DocumentStatus(document.status)
        except ValueError as exc:
            raise InvalidDocumentTransitionError(
                f"Unknown document status: {document.status}"
            ) from exc
        if current is not expected:
            raise InvalidDocumentTransitionError(
                f"Cannot transition document from {current.value} to {target.value}"
            )

        updated = self._repository.update_status(document_id, target)
        if updated is None:
            raise PipelineDocumentNotFoundError("Document not found")
        return updated
