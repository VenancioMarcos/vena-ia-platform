"""add request and correlation ids to audit events

Revision ID: a63d2f8c1b04
Revises: f42a1b7c9d30
Create Date: 2026-08-02
"""

import sqlalchemy as sa
from alembic import op

revision = "a63d2f8c1b04"
down_revision = "f42a1b7c9d30"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "security_audit_events", sa.Column("request_id", sa.String(36), nullable=True)
    )
    op.add_column(
        "security_audit_events", sa.Column("correlation_id", sa.String(36), nullable=True)
    )
    op.create_index(
        "ix_security_audit_events_request_id", "security_audit_events", ["request_id"]
    )
    op.create_index(
        "ix_security_audit_events_correlation_id",
        "security_audit_events",
        ["correlation_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_security_audit_events_correlation_id", table_name="security_audit_events")
    op.drop_index("ix_security_audit_events_request_id", table_name="security_audit_events")
    op.drop_column("security_audit_events", "correlation_id")
    op.drop_column("security_audit_events", "request_id")
