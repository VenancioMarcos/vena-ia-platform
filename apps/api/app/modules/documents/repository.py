from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.modules.documents.models import Document
from app.modules.documents.schemas import DocumentStatus


class DocumentRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def create(self, document: Document) -> Document:
        try:
            self._db.add(document)
            self._db.commit()
            self._db.refresh(document)
            return document
        except Exception:
            self._db.rollback()
            raise

    def get(self, document_id: str) -> Document | None:
        return self._db.get(Document, document_id)

    def list_documents(self, project_id: str) -> list[Document]:
        stmt = (
            select(Document)
            .where(Document.project_id == project_id)
            .order_by(Document.created_at)
        )
        return list(self._db.scalars(stmt))

    def list_by_project(self, project_id: str) -> list[Document]:
        return self.list_documents(project_id)

    def count_documents(self, project_id: str) -> int:
        stmt = select(func.count(Document.id)).where(Document.project_id == project_id)
        return self._db.scalar(stmt) or 0

    def exists(self, document_id: str) -> bool:
        stmt = select(Document.id).where(Document.id == document_id).limit(1)
        return self._db.scalar(stmt) is not None

    def exists_in_project(self, document_id: str, project_id: str) -> bool:
        stmt = (
            select(Document.id)
            .where(Document.id == document_id, Document.project_id == project_id)
            .limit(1)
        )
        return self._db.scalar(stmt) is not None

    def update_status(
        self, document_id: str, status: DocumentStatus
    ) -> Document | None:
        document = self.get(document_id)
        if document is None:
            return None
        document.status = status.value
        try:
            self._db.commit()
            self._db.refresh(document)
            return document
        except Exception:
            self._db.rollback()
            raise

    def get_by_status(self, status: DocumentStatus) -> list[Document]:
        stmt = (
            select(Document)
            .where(Document.status == status.value)
            .order_by(Document.created_at)
        )
        return list(self._db.scalars(stmt))

    def list_all(self) -> list[Document]:
        stmt = select(Document).order_by(Document.created_at)
        return list(self._db.scalars(stmt))

    def list_ready(self) -> list[Document]:
        return self.get_by_status(DocumentStatus.READY)

    def list_processing(self) -> list[Document]:
        return self.get_by_status(DocumentStatus.PROCESSING)

    def list_failed(self) -> list[Document]:
        return self.get_by_status(DocumentStatus.FAILED)

    def statistics(self) -> dict[str, int]:
        stmt = select(
            func.count(Document.id).label("total_documents"),
            func.coalesce(
                func.sum(case((Document.status == DocumentStatus.UPLOADED.value, 1), else_=0)),
                0,
            ).label("uploaded"),
            func.coalesce(
                func.sum(
                    case((Document.status == DocumentStatus.PROCESSING.value, 1), else_=0)
                ),
                0,
            ).label("processing"),
            func.coalesce(
                func.sum(case((Document.status == DocumentStatus.READY.value, 1), else_=0)),
                0,
            ).label("ready"),
            func.coalesce(
                func.sum(case((Document.status == DocumentStatus.FAILED.value, 1), else_=0)),
                0,
            ).label("failed"),
            func.coalesce(func.sum(Document.file_size), 0).label("total_storage_bytes"),
        )
        row = self._db.execute(stmt).one()
        return {key: int(value) for key, value in row._mapping.items()}

    def delete(self, document: Document) -> None:
        try:
            self._db.delete(document)
            self._db.commit()
        except Exception:
            self._db.rollback()
            raise
