"""add durable asynchronous jobs

Revision ID: b18e4c7d2a91
Revises: a63d2f8c1b04
Create Date: 2026-08-05
"""

import sqlalchemy as sa
from alembic import op

revision = "b18e4c7d2a91"
down_revision = "a63d2f8c1b04"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "jobs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("schema_version", sa.String(32), nullable=False),
        sa.Column("job_type", sa.String(64), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("owner_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("project_id", sa.String(36), sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("resource_id", sa.String(36), nullable=False),
        sa.Column("progress", sa.Integer(), nullable=False),
        sa.Column("attempt", sa.Integer(), nullable=False),
        sa.Column("max_attempts", sa.Integer(), nullable=False),
        sa.Column("timeout_seconds", sa.Integer(), nullable=False),
        sa.Column("idempotency_key", sa.String(128), nullable=False),
        sa.Column("request_id", sa.String(36), nullable=True),
        sa.Column("correlation_id", sa.String(36), nullable=True),
        sa.Column("error_code", sa.String(64), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("available_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancel_requested_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("progress >= 0 AND progress <= 100", name="ck_jobs_progress"),
        sa.CheckConstraint("attempt >= 0", name="ck_jobs_attempt"),
        sa.CheckConstraint("max_attempts >= 1", name="ck_jobs_max_attempts"),
        sa.CheckConstraint("timeout_seconds >= 1", name="ck_jobs_timeout_seconds"),
        sa.CheckConstraint(
            "status IN ('QUEUED','RUNNING','SUCCEEDED','FAILED','RETRY_SCHEDULED',"
            "'CANCELLATION_REQUESTED','CANCELLED','TIMED_OUT')",
            name="ck_jobs_status",
        ),
        sa.UniqueConstraint(
            "owner_id", "job_type", "idempotency_key", name="uq_jobs_idempotency_scope"
        ),
    )
    op.create_index("ix_jobs_owner_id", "jobs", ["owner_id"])
    op.create_index("ix_jobs_project_id", "jobs", ["project_id"])
    op.create_index("ix_jobs_resource_id", "jobs", ["resource_id"])
    op.create_index("ix_jobs_request_id", "jobs", ["request_id"])
    op.create_index("ix_jobs_correlation_id", "jobs", ["correlation_id"])
    op.create_index(
        "ix_jobs_owner_status_created", "jobs", ["owner_id", "status", "created_at"]
    )
    op.create_index(
        "ix_jobs_project_status_created", "jobs", ["project_id", "status", "created_at"]
    )
    op.create_index("ix_jobs_status_available", "jobs", ["status", "available_at"])


def downgrade() -> None:
    op.drop_table("jobs")
