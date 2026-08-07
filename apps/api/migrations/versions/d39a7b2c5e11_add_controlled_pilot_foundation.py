"""add controlled pilot organizational foundation

Revision ID: d39a7b2c5e11
Revises: c27f6d9e4a10
Create Date: 2026-08-06
"""

import sqlalchemy as sa
from alembic import op

revision = "d39a7b2c5e11"
down_revision = "c27f6d9e4a10"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "organizations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "teams",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "organization_id",
            sa.String(36),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("organization_id", "name", name="uq_team_organization_name"),
    )
    op.create_index("ix_teams_organization_id", "teams", ["organization_id"])
    op.create_table(
        "memberships",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "organization_id",
            sa.String(36),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.String(36),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "team_id",
            sa.String(36),
            sa.ForeignKey("teams.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column("role", sa.String(16), nullable=False),
        sa.Column("status", sa.String(16), nullable=False),
        sa.Column("created_by", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_memberships_organization_id", "memberships", ["organization_id"])
    op.create_index("ix_memberships_user_id", "memberships", ["user_id"])
    op.create_index("ix_memberships_team_id", "memberships", ["team_id"])
    op.create_index(
        "uq_membership_org_user_unscoped",
        "memberships",
        ["organization_id", "user_id"],
        unique=True,
        postgresql_where=sa.text("team_id IS NULL"),
        sqlite_where=sa.text("team_id IS NULL"),
    )
    op.create_index(
        "uq_membership_org_user_team",
        "memberships",
        ["organization_id", "user_id", "team_id"],
        unique=True,
        postgresql_where=sa.text("team_id IS NOT NULL"),
        sqlite_where=sa.text("team_id IS NOT NULL"),
    )
    op.create_table(
        "pilot_contexts",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "organization_id",
            sa.String(36),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "team_id",
            sa.String(36),
            sa.ForeignKey("teams.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("status", sa.String(40), nullable=False),
        sa.Column("owner_user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("scope", sa.String(1000), nullable=False),
        sa.Column("review_status", sa.String(40), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_pilot_contexts_organization_id", "pilot_contexts", ["organization_id"])
    op.create_index("ix_pilot_contexts_team_id", "pilot_contexts", ["team_id"])
    op.create_table(
        "pilot_readiness_checklists",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "pilot_context_id",
            sa.String(36),
            sa.ForeignKey("pilot_contexts.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("items", sa.JSON(), nullable=False),
        sa.Column("privacy", sa.JSON(), nullable=False),
        sa.Column("result", sa.String(40), nullable=False),
        sa.Column("updated_by", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_pilot_readiness_checklists_pilot_context_id",
        "pilot_readiness_checklists",
        ["pilot_context_id"],
    )


def downgrade() -> None:
    op.drop_table("pilot_readiness_checklists")
    op.drop_table("pilot_contexts")
    op.drop_table("memberships")
    op.drop_table("teams")
    op.drop_table("organizations")
