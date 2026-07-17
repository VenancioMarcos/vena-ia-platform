"""Request-scoped dependency construction for the Documents module."""

from typing import Annotated

from fastapi import Depends, Header, HTTPException
from minio import Minio
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
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


def get_current_user_id(
    x_user_id: Annotated[str | None, Header(alias="X-User-ID")] = None,
) -> str:
    if x_user_id is None or not x_user_id.strip():
        raise HTTPException(status_code=401, detail="Authentication required")
    return x_user_id.strip()


CurrentUserDependency = Annotated[str, Depends(get_current_user_id)]


def get_document_service(
    repository: DocumentRepositoryDependency,
    storage: DocumentStorageDependency,
    db: DatabaseDependency,
    current_user_id: CurrentUserDependency,
    pipeline: DocumentPipelineDependency,
) -> DocumentService:
    return DocumentService(
        repository,
        storage,
        db,
        settings.document_max_file_size,
        current_user_id,
        pipeline,
    )


DocumentServiceDependency = Annotated[DocumentService, Depends(get_document_service)]
