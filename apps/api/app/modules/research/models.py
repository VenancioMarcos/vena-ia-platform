import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, ForeignKey, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


def _uuid() -> str:
    return str(uuid.uuid4())


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ResearchArticle(Base):
    __tablename__ = "research_articles"
    __table_args__ = (
        UniqueConstraint("document_id", name="uq_research_articles_document_id"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    project_id: Mapped[str] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    document_id: Mapped[str] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    created_by: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    title: Mapped[str | None] = mapped_column(String(500))
    authors: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    year: Mapped[int | None] = mapped_column(Integer)
    venue: Mapped[str | None] = mapped_column(String(500))
    volume: Mapped[str | None] = mapped_column(String(50))
    issue: Mapped[str | None] = mapped_column(String(50))
    pages: Mapped[str | None] = mapped_column(String(100))
    doi: Mapped[str | None] = mapped_column(String(255))
    keywords: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    abstract: Mapped[str | None] = mapped_column(Text)
    document_type: Mapped[str] = mapped_column(String(50), nullable=False)
    language: Mapped[str | None] = mapped_column(String(20))
    metadata_status: Mapped[str] = mapped_column(String(50), nullable=False)
    metadata_source: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False, default=_utcnow, onupdate=_utcnow
    )


class ResearchReference(Base):
    __tablename__ = "research_references"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    article_id: Mapped[str] = mapped_column(
        ForeignKey("research_articles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    authors: Mapped[str | None] = mapped_column(Text)
    title: Mapped[str | None] = mapped_column(String(500))
    year: Mapped[int | None] = mapped_column(Integer)
    venue: Mapped[str | None] = mapped_column(String(500))
    doi: Mapped[str | None] = mapped_column(String(255))
    page_number: Mapped[int] = mapped_column(Integer, nullable=False)
    extraction_method: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=_utcnow)


class DOEStudy(Base):
    __tablename__ = "doe_studies"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    project_id: Mapped[str] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    created_by: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    objective: Mapped[str] = mapped_column(Text, nullable=False)
    response_variables: Mapped[list[dict[str, object]]] = mapped_column(JSON, nullable=False)
    factors: Mapped[list[dict[str, object]]] = mapped_column(JSON, nullable=False)
    design_type: Mapped[str] = mapped_column(String(50), nullable=False)
    repetitions: Mapped[int] = mapped_column(Integer, nullable=False)
    randomization_required: Mapped[bool] = mapped_column(Boolean, nullable=False)
    blocking_notes: Mapped[str | None] = mapped_column(Text)
    assumptions: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    status: Mapped[str] = mapped_column(String(80), nullable=False)
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False, default=_utcnow, onupdate=_utcnow
    )


class ANOVADataset(Base):
    __tablename__ = "anova_datasets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    project_id: Mapped[str] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    created_by: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    factor_name: Mapped[str] = mapped_column(String(255), nullable=False)
    response_name: Mapped[str] = mapped_column(String(255), nullable=False)
    response_unit: Mapped[str] = mapped_column(String(100), nullable=False)
    observations: Mapped[list[dict[str, object]]] = mapped_column(JSON, nullable=False)
    descriptive_summary: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    assumptions_checklist: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    status: Mapped[str] = mapped_column(String(80), nullable=False)
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=_utcnow)


class ResearchReport(Base):
    __tablename__ = "research_reports"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    project_id: Mapped[str] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    created_by: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    report_type: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    objective: Mapped[str] = mapped_column(Text, nullable=False)
    document_ids: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    synthesis: Mapped[str] = mapped_column(Text, nullable=False)
    evidence: Mapped[list[dict[str, object]]] = mapped_column(JSON, nullable=False)
    limitations: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=_utcnow)
