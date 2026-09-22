import hashlib
import json
from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modules.documents.models import Document
from app.modules.engineering.controlled_environment_schemas import (
    ControlledDownloadRequest,
    ControlledEnvironmentRequest,
    ControlledEnvironmentResult,
)
from app.modules.product_flow.models import ControlledResultRecord, ResultFeedback
from app.modules.product_flow.schemas import FeedbackCreate, HumanReviewRequest
from app.modules.projects.models import Project
from app.modules.users.models import User


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _hash_json(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest()


def _token_hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


class ProductFlowService:
    def __init__(self, db: Session, user: User) -> None:
        self.db = db
        self.user = user

    def record_result(
        self,
        request: ControlledEnvironmentRequest,
        result: ControlledEnvironmentResult,
    ) -> ControlledResultRecord:
        document = self.db.get(Document, request.planning.document_id)
        project = self.db.get(Project, document.project_id) if document is not None else None
        # The controlled CAD service has already enforced document access for the
        # current user. Requiring project ownership again here would incorrectly
        # reject organization members authorized by that upstream boundary.
        if document is None or project is None:
            raise HTTPException(status_code=404, detail="Document not found")
        record = ControlledResultRecord(
            organization_id=request.organization_id,
            project_id=project.id,
            document_id=document.id,
            created_by=self.user.id,
            result_version=result.schema_version,
            gcode_hash=_hash_json(result.gcode_candidate.model_dump(mode="json")),
            digital_thread_hash=_hash_json(result.digital_thread.model_dump(mode="json")),
            blind_validation_hash=_hash_json(result.blind_validation.model_dump(mode="json")),
            download_token_hash=_token_hash(result.download_token),
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def get_result(self, result_id: str) -> ControlledResultRecord:
        record = self.db.scalar(
            select(ControlledResultRecord).where(
                ControlledResultRecord.id == result_id,
                ControlledResultRecord.created_by == self.user.id,
            )
        )
        if record is None:
            raise HTTPException(status_code=404, detail="Controlled result not found")
        return record

    def approve_review(
        self, result_id: str, payload: HumanReviewRequest
    ) -> ControlledResultRecord:
        record = self.get_result(result_id)
        record.review_state = "APPROVED_FOR_CONTROLLED_DOWNLOAD"
        record.review_note = payload.note
        record.reviewed_by = self.user.id
        record.reviewed_at = _utcnow()
        record.updated_at = record.reviewed_at
        self.db.commit()
        self.db.refresh(record)
        return record

    def require_download_approval(self, payload: ControlledDownloadRequest) -> None:
        record = self.get_result(payload.result_id)
        expected = {
            "organization": payload.organization_id,
            "gcode": _hash_json(payload.gcode_candidate.model_dump(mode="json")),
            "thread": _hash_json(payload.digital_thread.model_dump(mode="json")),
            "blind": _hash_json(payload.blind_validation.model_dump(mode="json")),
            "token": _token_hash(payload.download_token),
        }
        actual = {
            "organization": record.organization_id,
            "gcode": record.gcode_hash,
            "thread": record.digital_thread_hash,
            "blind": record.blind_validation_hash,
            "token": record.download_token_hash,
        }
        if expected != actual:
            raise HTTPException(status_code=422, detail="Controlled result binding mismatch")
        if record.review_state != "APPROVED_FOR_CONTROLLED_DOWNLOAD":
            raise HTTPException(status_code=409, detail="Persisted human review is required")

    def create_feedback(self, result_id: str, payload: FeedbackCreate) -> ResultFeedback:
        record = self.get_result(result_id)
        if record.review_state != "APPROVED_FOR_CONTROLLED_DOWNLOAD":
            raise HTTPException(status_code=409, detail="Review must be completed before feedback")
        feedback = ResultFeedback(
            result_id=record.id,
            project_id=record.project_id,
            result_version=record.result_version,
            rating=payload.rating,
            comment=payload.comment,
            created_by=self.user.id,
        )
        self.db.add(feedback)
        try:
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise HTTPException(status_code=409, detail="Feedback already submitted") from exc
        self.db.refresh(feedback)
        return feedback

    def get_feedback(self, result_id: str) -> ResultFeedback:
        self.get_result(result_id)
        feedback = self.db.scalar(
            select(ResultFeedback).where(
                ResultFeedback.result_id == result_id,
                ResultFeedback.created_by == self.user.id,
            )
        )
        if feedback is None:
            raise HTTPException(status_code=404, detail="Feedback not found")
        return feedback
