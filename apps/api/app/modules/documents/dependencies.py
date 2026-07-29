"""Request-scoped dependency construction for the Documents module."""

from typing import Annotated

from fastapi import Depends
from minio import Minio
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.modules.auth.dependencies import CurrentUserDependency
from app.modules.documents.repository import DocumentRepository
from app.modules.documents.pipeline import DocumentPipeline
from app.modules.documents.service import DocumentService
from app.modules.documents.storage import DocumentStorage, MinIOStorage

DatabaseDependency = Annotated[Session, Depends(get_db)]


def get_document_repository(db: DatabaseDependency) -> DocumentRepository:
    return DocumentRepository(db)


DocumentRepositoryDependency = Annotated[
    DocumentRepository, Depends(get_document_repository)
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
