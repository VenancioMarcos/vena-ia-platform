import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, ForeignKey, Index, String, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


def _uuid() -> str:
    return str(uuid.uuid4())


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="ACTIVE")
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(nullable=False, default=_utcnow)


class Team(Base):
    __tablename__ = "teams"
    __table_args__ = (
        UniqueConstraint("organization_id", "name", name="uq_team_organization_name"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    organization_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="ACTIVE")
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(nullable=False, default=_utcnow)


class Membership(Base):
    __tablename__ = "memberships"
    __table_args__ = (
        Index(
            "uq_membership_org_user_unscoped",
            "organization_id",
            "user_id",
            unique=True,
            sqlite_where=text("team_id IS NULL"),
            postgresql_where=text("team_id IS NULL"),
        ),
        Index(
            "uq_membership_org_user_team",
            "organization_id",
            "user_id",
            "team_id",
            unique=True,
            sqlite_where=text("team_id IS NOT NULL"),
            postgresql_where=text("team_id IS NOT NULL"),
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    organization_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    team_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("teams.id", ondelete="CASCADE"), nullable=True, index=True
    )
    role: Mapped[str] = mapped_column(String(16), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="ACTIVE")
    created_by: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(nullable=False, default=_utcnow)
    revoked_at: Mapped[datetime | None] = mapped_column(nullable=True)


class PilotContext(Base):
    __tablename__ = "pilot_contexts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    organization_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    team_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("teams.id", ondelete="SET NULL"), nullable=True, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="DRAFT")
    owner_user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    scope: Mapped[str] = mapped_column(String(1000), nullable=False)
    review_status: Mapped[str] = mapped_column(
        String(40), nullable=False, default="HUMAN_REVIEW_REQUIRED"
    )
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(nullable=False, default=_utcnow)


class PilotReadinessChecklist(Base):
    __tablename__ = "pilot_readiness_checklists"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    pilot_context_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("pilot_contexts.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    items: Mapped[list[dict[str, str]]] = mapped_column(JSON, nullable=False)
    privacy: Mapped[dict[str, bool]] = mapped_column(JSON, nullable=False)
    result: Mapped[str] = mapped_column(String(40), nullable=False, default="INCOMPLETE")
    updated_by: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(nullable=False, default=_utcnow)
