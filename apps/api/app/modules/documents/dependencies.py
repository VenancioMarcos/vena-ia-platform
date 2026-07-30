"""Request-scoped dependency construction for the Documents module."""

from typing import Annotated

from fastapi import Depends
from minio import Minio
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.modules.ai.dependencies import AIServiceDependency
from app.modules.auth.dependencies import AuthorizationDependency, CurrentUserDependency
from app.modules.documents.chunking import CharacterTextChunker
from app.modules.documents.contracts import ChunkingStrategy, TextExtractor
from app.modules.documents.extraction import PdfTextExtractor
from app.modules.documents.knowledge import KnowledgeService
from app.modules.documents.pipeline import DocumentPipeline
from app.modules.documents.processing import DocumentProcessingService
from app.modules.documents.repository import DocumentChunkRepository, DocumentRepository
from app.modules.documents.service import DocumentService
from app.modules.documents.storage import DocumentStorage, MinIOStorage

DatabaseDependency = Annotated[Session, Depends(get_db)]


def get_document_repository(db: DatabaseDependency) -> DocumentRepository:
    return DocumentRepository(db)


DocumentRepositoryDependency = Annotated[
    DocumentRepository, Depends(get_document_repository)
]


def get_document_chunk_repository(db: DatabaseDependency) -> DocumentChunkRepository:
    return DocumentChunkRepository(db)


DocumentChunkRepositoryDependency = Annotated[
    DocumentChunkRepository,
    Depends(get_document_chunk_repository),
]


def get_document_pipeline(
    repository: DocumentRepositoryDependency,
) -> DocumentPipeline:
    return DocumentPipeline(repository)


DocumentPipelineDependency = Annotated[DocumentPipeline, Depends(get_document_pipeline)]


def get_document_storage() -> DocumentStorage:
    client = Minio(
        settings.minio_endpoint,
        access_key=settings.minio_access_key,
        secret_key=settings.minio_secret_key,
        secure=settings.minio_secure,
    )
    return MinIOStorage(client, settings.minio_bucket)


DocumentStorageDependency = Annotated[DocumentStorage, Depends(get_document_storage)]


def initialize_document_storage() -> None:
    get_document_storage().initialize()


def get_document_service(
    repository: DocumentRepositoryDependency,
    storage: DocumentStorageDependency,
    db: DatabaseDependency,
    current_user: CurrentUserDependency,
    pipeline: DocumentPipelineDependency,
) -> DocumentService:
    return DocumentService(
        repository,
        storage,
        db,
        settings.document_max_file_size,
        current_user,
        pipeline,
    )


DocumentServiceDependency = Annotated[DocumentService, Depends(get_document_service)]


def get_pdf_text_extractor() -> TextExtractor:
    return PdfTextExtractor()


TextExtractorDependency = Annotated[TextExtractor, Depends(get_pdf_text_extractor)]


def get_text_chunker() -> ChunkingStrategy:
    return CharacterTextChunker(
        chunk_size=settings.rag_chunk_size,
        overlap=settings.rag_chunk_overlap,
    )


ChunkingStrategyDependency = Annotated[
    ChunkingStrategy,
    Depends(get_text_chunker),
]


def get_document_processing_service(
    document_service: DocumentServiceDependency,
    chunk_repository: DocumentChunkRepositoryDependency,
    storage: DocumentStorageDependency,
    extractor: TextExtractorDependency,
    chunker: ChunkingStrategyDependency,
) -> DocumentProcessingService:
    return DocumentProcessingService(
        document_service=document_service,
        chunk_repository=chunk_repository,
        storage=storage,
        extractor=extractor,
        chunker=chunker,
    )


DocumentProcessingServiceDependency = Annotated[
    DocumentProcessingService,
    Depends(get_document_processing_service),
]


def get_knowledge_service(
    document_service: DocumentServiceDependency,
    authorization: AuthorizationDependency,
    chunk_repository: DocumentChunkRepositoryDependency,
    ai_service: AIServiceDependency,
) -> KnowledgeService:
    return KnowledgeService(
        document_service=document_service,
        authorization=authorization,
        chunk_repository=chunk_repository,
        ai_service=ai_service,
        provider=settings.rag_ai_provider,
        embedding_model=settings.rag_embedding_model,
        chat_model=settings.rag_chat_model,
        embedding_dimensions=settings.rag_embedding_dimensions,
    )


KnowledgeServiceDependency = Annotated[
    KnowledgeService,
    Depends(get_knowledge_service),
]
