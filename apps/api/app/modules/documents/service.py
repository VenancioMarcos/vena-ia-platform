import re
import unicodedata
import uuid
from collections.abc import Callable

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.modules.documents.models import Document
from app.modules.documents.pipeline import (
    DocumentPipeline,
    PipelineDocumentNotFoundError,
)
from app.modules.documents.repository import DocumentRepository
from app.modules.documents.schemas import DocumentStatus
from app.modules.documents.storage import DocumentStorage, StorageError
from app.modules.projects.models import Project
from app.modules.users.models import User


class DocumentNotFoundError(Exception):
    pass


class ProjectNotFoundError(Exception):
    pass


class InvalidDocumentError(Exception):
    pass


class DocumentStorageError(Exception):
    pass


class DocumentAccessDeniedError(Exception):
    pass


class DocumentTooLargeError(InvalidDocumentError):
    pass


class DocumentProjectMismatchError(Exception):
    pass


class DocumentAdministrationDeniedError(Exception):
    pass


class DocumentService:
    def __init__(
        self,
        repository: DocumentRepository,
        storage: DocumentStorage,
        db: Session,
        max_file_size: int,
        current_user_id: str,
        pipeline: DocumentPipeline,
    ) -> None:
        self._repository = repository
        self._storage = storage
        self._db = db
        self._max_file_size = max_file_size
        self._current_user_id = current_user_id
        self._pipeline = pipeline

    def create(self, project_id: str, file: UploadFile) -> Document:
        self._require_project_access(project_id)
        filename, content_type, file_size = self._validate_file(file)
        document_id = str(uuid.uuid4())
        storage_path = f"projects/{project_id}/documents/{document_id}/{filename}"

        try:
            self._storage.upload_file(
                storage_path=storage_path,
                data=file.file,
                file_size=file_size,
                content_type=content_type,
            )
        except StorageError as exc:
            raise DocumentStorageError("Document storage unavailable") from exc

        document = Document(
            id=document_id,
            project_id=project_id,
            filename=filename,
            content_type=content_type,
            file_size=file_size,
            storage_path=storage_path,
            status=DocumentStatus.UPLOADED.value,
        )
        try:
            return self._repository.create(document)
        except Exception:
            try:
                self._storage.delete_file(storage_path)
            except StorageError as exc:
                raise DocumentStorageError("Document rollback failed") from exc
            raise

    def get(self, document_id: str) -> Document:
        document = self._repository.get(document_id)
        if document is None:
            raise DocumentNotFoundError("Document not found")
        self._require_project_access(document.project_id)
        return document

    def list_documents(self, project_id: str) -> list[Document]:
        self._require_project_access(project_id)
        return self._repository.list_documents(project_id)

    def list_by_project(self, project_id: str) -> list[Document]:
        return self.list_documents(project_id)

    def count_documents(self, project_id: str) -> int:
        self._require_project_access(project_id)
        return self._repository.count_documents(project_id)

    def remove_document(self, project_id: str, document_id: str) -> None:
        self._require_project_access(project_id)
        if not self._repository.exists(document_id):
            raise DocumentNotFoundError("Document not found")
        if not self._repository.exists_in_project(document_id, project_id):
            raise DocumentProjectMismatchError("Document does not belong to project")

        document = self._repository.get(document_id)
        if document is None:
            raise DocumentNotFoundError("Document not found")
        self._remove_stored_document(document)

    def process_document(self, document_id: str) -> Document:
        self.get(document_id)
        return self._run_pipeline_transition(self._pipeline.enqueue, document_id)

    def start_processing(self, document_id: str) -> Document:
        self.get(document_id)
        return self._run_pipeline_transition(self._pipeline.start_processing, document_id)

    def finish_processing(self, document_id: str) -> Document:
        self.get(document_id)
        return self._run_pipeline_transition(self._pipeline.finish_processing, document_id)

    def fail_processing(self, document_id: str) -> Document:
        self.get(document_id)
        return self._run_pipeline_transition(self._pipeline.fail_processing, document_id)

    def list_all_documents(self) -> list[Document]:
        self._require_admin()
        return self._repository.list_all()

    def list_ready_documents(self) -> list[Document]:
        self._require_admin()
        return self._repository.list_ready()

    def list_processing_documents(self) -> list[Document]:
        self._require_admin()
        return self._repository.list_processing()

    def list_failed_documents(self) -> list[Document]:
        self._require_admin()
        return self._repository.list_failed()

    def document_statistics(self) -> dict[str, int]:
        self._require_admin()
        return self._repository.statistics()

    def delete(self, document_id: str) -> None:
        document = self._repository.get(document_id)
        if document is None:
            return
        self._require_project_access(document.project_id)
        self._remove_stored_document(document)

    def _remove_stored_document(self, document: Document) -> None:
        try:
            self._storage.delete_file(document.storage_path)
        except StorageError as exc:
            raise DocumentStorageError("Document storage unavailable") from exc
        self._repository.delete(document)

    @staticmethod
    def _run_pipeline_transition(
        operation: Callable[[str], Document], document_id: str
    ) -> Document:
        try:
            return operation(document_id)
        except PipelineDocumentNotFoundError as exc:
            raise DocumentNotFoundError(str(exc)) from exc

    def _require_project_access(self, project_id: str) -> Project:
        project = self._db.get(Project, project_id)
        if project is None:
            raise ProjectNotFoundError("Project not found")
        if project.owner_id != self._current_user_id:
            raise DocumentAccessDeniedError("Document access denied")
        return project

    def _require_admin(self) -> User:
        user = self._db.get(User, self._current_user_id)
        if user is None or user.role.lower() != "admin":
            raise DocumentAdministrationDeniedError("Administrative access required")
        return user

    def _validate_file(self, file: UploadFile) -> tuple[str, str, int]:
        filename = self._sanitize_filename(file.filename or "")
        if filename is None:
            raise InvalidDocumentError("Filename is required")

        content_type = (file.content_type or "").split(";", 1)[0].strip().lower()
        if not re.fullmatch(r"[a-z0-9!#$&^_.+-]+/[a-z0-9!#$&^_.+-]+", content_type):
            raise InvalidDocumentError("Valid content type is required")

        try:
            file.file.seek(0, 2)
            file_size = file.file.tell()
            file.file.seek(0)
        except (OSError, ValueError) as exc:
            raise InvalidDocumentError("Unable to read file") from exc

        if file_size <= 0:
            raise InvalidDocumentError("File must not be empty")
        if file_size > self._max_file_size:
            raise DocumentTooLargeError("File exceeds the configured size limit")

        return filename, content_type, file_size

    @staticmethod
    def _sanitize_filename(original: str) -> str | None:
        basename = original.replace("\\", "/").rsplit("/", 1)[-1].strip()
        normalized = unicodedata.normalize("NFKC", basename)
        sanitized = re.sub(r"[^A-Za-z0-9._-]", "_", normalized).strip(". ")
        sanitized = re.sub(r"_+", "_", sanitized)[:255]
        if not sanitized or sanitized in {".", ".."}:
            return None

        stem = sanitized.rsplit(".", 1)[0].upper()
        if stem in {"CON", "PRN", "AUX", "NUL"} or re.fullmatch(
            r"(?:COM|LPT)[1-9]", stem
        ):
            sanitized = f"_{sanitized}"
        return sanitized[:255]
