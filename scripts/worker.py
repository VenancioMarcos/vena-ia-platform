"""Dedicated worker process for allowlisted asynchronous Vena_IA jobs."""

from __future__ import annotations

import logging
import os
import signal
import socket
import time
from collections.abc import Callable

from app.core import models_registry  # noqa: F401  (registers ORM models in worker process)
from app.core.alerts import AlertManager, NoOpAlertProvider
from app.core.config import settings
from app.core.database import SessionLocal
from app.core.metrics import InMemoryMetricCollector, NoOpMetricCollector
from app.core.tracing import NoOpTraceProvider, Tracer
from app.modules.ai.dependencies import get_ai_service, get_provider_factory
from app.modules.auth.authorization import AuthorizationService
from app.modules.documents.chunking import CharacterTextChunker
from app.modules.documents.dependencies import get_document_storage
from app.modules.documents.extraction import (
    PdfExtractionCancelled,
    PdfExtractionError,
    PdfTextExtractor,
)
from app.modules.documents.knowledge import KnowledgeService
from app.modules.documents.pipeline import DocumentPipeline
from app.modules.documents.processing import (
    DocumentContentUnavailableError,
    DocumentProcessingError,
    DocumentProcessingService,
)
from app.modules.documents.repository import DocumentChunkRepository, DocumentRepository
from app.modules.documents.schemas import DocumentStatus
from app.modules.documents.service import DocumentService
from app.modules.jobs.contracts import JobType
from app.modules.jobs.dependencies import build_job_queue
from app.modules.jobs.models import Job
from app.modules.jobs.worker import JobHandler, JobWorker, SafeJobExecutionError
from app.modules.users.models import User

_stopping = False


def _stop(_signum: int, _frame: object) -> None:
    global _stopping
    _stopping = True


def _document_handler() -> JobHandler:
    def handle(job: Job, progress: Callable[[int], None], cancelled: Callable[[], bool]) -> None:
        if cancelled():
            return
        progress(10)
        db = SessionLocal()
        try:
            owner = db.get(User, job.owner_id)
            if owner is None:
                raise SafeJobExecutionError(
                    "RESOURCE_NOT_FOUND", "Job resource is unavailable", retryable=False
                )
            repository = DocumentRepository(db)
            document = repository.get(job.resource_id)
            if document is None or document.project_id != job.project_id:
                raise SafeJobExecutionError(
                    "RESOURCE_NOT_FOUND", "Job resource is unavailable", retryable=False
                )
            storage = get_document_storage()
            document_service = DocumentService(
                repository,
                storage,
                db,
                settings.document_max_file_size,
                owner,
                DocumentPipeline(repository),
            )
            progress(25)
            processing = DocumentProcessingService(
                document_service,
                DocumentChunkRepository(db),
                storage,
                PdfTextExtractor(),
                CharacterTextChunker(
                    chunk_size=settings.rag_chunk_size,
                    overlap=settings.rag_chunk_overlap,
                ),
            )
            if document.status != DocumentStatus.READY.value:
                try:
                    processing.process(
                        document.id,
                        mark_ready=False,
                        page_progress=lambda current, total: progress(
                            25 + int((current / max(total, 1)) * 35)
                        ),
                        cancelled=cancelled,
                    )
                except PdfExtractionCancelled:
                    return
                except PdfExtractionError as exc:
                    raise SafeJobExecutionError(exc.code, str(exc), retryable=False) from exc
                except DocumentContentUnavailableError as exc:
                    raise SafeJobExecutionError(
                        "DEPENDENCY_UNAVAILABLE",
                        "Document storage is temporarily unavailable",
                        retryable=True,
                    ) from exc
                except DocumentProcessingError as exc:
                    raise SafeJobExecutionError(
                        "INTERNAL_PROCESSING_ERROR",
                        "Document processing failed safely",
                        retryable=True,
                    ) from exc
            if cancelled():
                current = repository.get(document.id)
                if current is not None and current.status == DocumentStatus.PROCESSING.value:
                    document_service.fail_processing(document.id)
                return
            progress(70)
            try:
                KnowledgeService(
                    document_service=document_service,
                    authorization=AuthorizationService(db, owner),
                    chunk_repository=DocumentChunkRepository(db),
                    ai_service=get_ai_service(get_provider_factory()),
                    provider=settings.rag_ai_provider,
                    embedding_model=settings.rag_embedding_model,
                    chat_model=settings.rag_chat_model,
                    embedding_dimensions=settings.rag_embedding_dimensions,
                    allow_processing=True,
                ).index_document(document.id)
            except Exception as exc:
                current = repository.get(document.id)
                if current is not None and current.status == DocumentStatus.PROCESSING.value:
                    document_service.fail_processing(document.id)
                raise SafeJobExecutionError(
                    "DEPENDENCY_UNAVAILABLE",
                    "Indexing dependency is temporarily unavailable",
                    retryable=True,
                ) from exc
            current = repository.get(document.id)
            if current is not None and current.status == DocumentStatus.PROCESSING.value:
                document_service.finish_processing(document.id)
            progress(95)
        finally:
            db.close()

    return handle


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
    signal.signal(signal.SIGINT, _stop)
    signal.signal(signal.SIGTERM, _stop)
    worker = JobWorker(
        SessionLocal,
        build_job_queue(),
        {JobType.DOCUMENT_PROCESSING.value: _document_handler()},
        worker_id=f"{socket.gethostname()}-{os.getpid()}",
        lease_seconds=settings.jobs_lease_seconds,
        retry_base_seconds=settings.jobs_retry_base_seconds,
        retry_max_seconds=settings.jobs_retry_max_seconds,
        retry_jitter_ratio=settings.jobs_retry_jitter_ratio,
        metric_collector=(
            InMemoryMetricCollector()
            if settings.observability_collection_enabled
            else NoOpMetricCollector()
        ),
        alert_manager=AlertManager(NoOpAlertProvider()),
        tracer=Tracer(NoOpTraceProvider()),
    )
    while not _stopping:
        result = worker.run_once()
        if result.outcome == "idle":
            time.sleep(0.5)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
