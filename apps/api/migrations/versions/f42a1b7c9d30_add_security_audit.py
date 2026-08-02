"""add security audit and authentication version

Revision ID: f42a1b7c9d30
Revises: e15a7c9d4f20
Create Date: 2026-08-02
"""

import sqlalchemy as sa
from alembic import op

revision = "f42a1b7c9d30"
down_revision = "e15a7c9d4f20"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("auth_version", sa.Integer(), nullable=False, server_default="0"),
    )
    op.create_table(
        "security_audit_events",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("event_type", sa.String(64), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("actor_user_id", sa.String(36), nullable=True),
        sa.Column("target_user_id", sa.String(36), nullable=True),
        sa.Column("outcome", sa.String(32), nullable=False),
        sa.Column("reason", sa.String(64), nullable=True),
        sa.Column("origin", sa.String(255), nullable=False),
        sa.ForeignKeyConstraint(["actor_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["target_user_id"], ["users.id"]),
    )
    op.create_index("ix_security_audit_events_occurred_at", "security_audit_events", ["occurred_at"])
    op.create_index("ix_security_audit_events_actor_user_id", "security_audit_events", ["actor_user_id"])
    op.create_index("ix_security_audit_events_target_user_id", "security_audit_events", ["target_user_id"])
    op.create_index("ix_security_audit_events_type_time", "security_audit_events", ["event_type", "occurred_at"])


def downgrade() -> None:
    op.drop_index("ix_security_audit_events_type_time", table_name="security_audit_events")
    op.drop_index("ix_security_audit_events_target_user_id", table_name="security_audit_events")
    op.drop_index("ix_security_audit_events_actor_user_id", table_name="security_audit_events")
    op.drop_index("ix_security_audit_events_occurred_at", table_name="security_audit_events")
    op.drop_table("security_audit_events")
    op.drop_column("users", "auth_version")
