"""Synchronous PDF ingestion foundation for the v0.5 RAG pipeline."""

from app.modules.documents.contracts import (
    ChunkingStrategy,
    ChunkRepositoryContract,
    ExtractedPage,
    ProcessingResult,
    TextExtractor,
)
from app.modules.documents.extraction import PdfExtractionError
from app.modules.documents.models import DocumentChunk
from app.modules.documents.schemas import DocumentStatus
from app.modules.documents.service import DocumentService
from app.modules.documents.storage import DocumentStorage, StorageError
from app.core.metrics import MetricCollector, safe_metric_call


class DocumentContentUnavailableError(Exception):
    pass


class DocumentProcessingError(Exception):
    pass


class DocumentProcessingService:
    def __init__(
        self,
        document_service: DocumentService,
        chunk_repository: ChunkRepositoryContract,
        storage: DocumentStorage,
        extractor: TextExtractor,
        chunker: ChunkingStrategy,
        metric_collector: MetricCollector | None = None,
    ) -> None:
        self._document_service = document_service
        self._chunk_repository = chunk_repository
        self._storage = storage
        self._extractor = extractor
        self._chunker = chunker
        self._metric_collector = metric_collector

    def process(self, document_id: str) -> ProcessingResult:
        document = self._document_service.get(document_id)
        if self._metric_collector is not None:
            safe_metric_call(
                self._metric_collector.increment,
                "processing_jobs_total",
                {"operation": "document.processing", "outcome": "started"},
            )
            if document.status == DocumentStatus.FAILED.value:
                safe_metric_call(
                    self._metric_collector.increment,
                    "retry_attempts_total",
                    {"operation": "document.processing"},
                )
        self._document_service.start_processing(document_id)

        try:
            content = self._storage.download_file(document.storage_path)
            pages = self._extractor.extract_pages(content)
            chunks = self._build_chunks(document_id, pages)
            if not chunks:
                raise PdfExtractionError("PDF does not contain extractable text")
            persisted = self._chunk_repository.replace_for_document(document_id, chunks)
            ready_document = self._document_service.finish_processing(document_id)
            return ProcessingResult(
                document=ready_document,
                chunk_count=len(persisted),
            )
        except StorageError as exc:
            self._mark_failed(document_id)
            raise DocumentContentUnavailableError(
                "Document storage unavailable"
            ) from exc
        except PdfExtractionError:
            self._mark_failed(document_id)
            raise
        except Exception as exc:
            self._mark_failed(document_id)
            raise DocumentProcessingError("Document processing failed") from exc

    def list_chunks(
        self,
        document_id: str,
        page_number: int | None = None,
    ) -> list[DocumentChunk]:
        self._document_service.get(document_id)
        return self._chunk_repository.list_for_document(document_id, page_number)

    def _build_chunks(
        self,
        document_id: str,
        pages: list[ExtractedPage],
    ) -> list[DocumentChunk]:
        chunks: list[DocumentChunk] = []
        for page in pages:
            for fragment in self._chunker.split(page.text):
                chunks.append(
                    DocumentChunk(
                        document_id=document_id,
                        page_number=page.page_number,
                        chunk_index=len(chunks),
                        start_offset=fragment.start_offset,
                        end_offset=fragment.end_offset,
                        character_count=len(fragment.content),
                        content=fragment.content,
                    )
                )
        return chunks

    def _mark_failed(self, document_id: str) -> None:
        try:
            self._document_service.fail_processing(document_id)
        except Exception:
            pass
