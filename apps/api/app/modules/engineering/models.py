import uuid
from datetime import datetime, timezone

from sqlalchemy import CheckConstraint, Index, JSON, ForeignKey, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


def _uuid() -> str:
    return str(uuid.uuid4())


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class EngineeringCatalogItem(Base):
    __tablename__ = "engineering_catalog_items"
    __table_args__ = (
        CheckConstraint(
            "scope_type IN ('SYSTEM_REFERENCE', 'ORGANIZATION_OWNED', 'LEGACY_UNSCOPED')",
            name="ck_engineering_catalog_scope_type",
        ),
        CheckConstraint(
            "(scope_type = 'ORGANIZATION_OWNED' AND organization_id IS NOT NULL) OR "
            "(scope_type != 'ORGANIZATION_OWNED' AND organization_id IS NULL)",
            name="ck_engineering_catalog_scope_owner",
        ),
        Index(
            "uq_engineering_catalog_organization_version",
            "organization_id",
            "kind",
            "code",
            "data_version",
            unique=True,
            postgresql_where=text("scope_type = 'ORGANIZATION_OWNED'"),
            sqlite_where=text("scope_type = 'ORGANIZATION_OWNED'"),
        ),
        Index(
            "uq_engineering_catalog_system_version",
            "kind",
            "code",
            "data_version",
            unique=True,
            postgresql_where=text("scope_type = 'SYSTEM_REFERENCE'"),
            sqlite_where=text("scope_type = 'SYSTEM_REFERENCE'"),
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    kind: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    code: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    data_version: Mapped[str] = mapped_column(String(64), nullable=False)
    source: Mapped[str] = mapped_column(Text, nullable=False)
    properties: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    scope_type: Mapped[str] = mapped_column(
        String(32), nullable=False, default="LEGACY_UNSCOPED", index=True
    )
    organization_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("organizations.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    created_by: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=_utcnow)
