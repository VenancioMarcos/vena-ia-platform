"""add persisted review and feedback for the public product flow

Revision ID: a71c9e4d2b80
Revises: e61c4f8a2b90
Create Date: 2026-09-21
"""

import sqlalchemy as sa
from alembic import op

revision = "a71c9e4d2b80"
down_revision = "e61c4f8a2b90"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "controlled_result_records",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("organization_id", sa.String(36), nullable=False),
        sa.Column("project_id", sa.String(36), nullable=False),
        sa.Column("document_id", sa.String(36), nullable=False),
        sa.Column("created_by", sa.String(36), nullable=False),
        sa.Column("result_version", sa.String(64), nullable=False),
        sa.Column("gcode_hash", sa.String(64), nullable=False),
        sa.Column("digital_thread_hash", sa.String(64), nullable=False),
        sa.Column("blind_validation_hash", sa.String(64), nullable=False),
        sa.Column("download_token_hash", sa.String(64), nullable=False, unique=True),
        sa.Column(
            "review_state",
            sa.String(48),
            nullable=False,
            server_default="REQUIRES_HUMAN_REVIEW",
        ),
        sa.Column("review_note", sa.Text(), nullable=True),
        sa.Column("reviewed_by", sa.String(36), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "review_state IN ('REQUIRES_HUMAN_REVIEW', "
            "'APPROVED_FOR_CONTROLLED_DOWNLOAD')",
            name="ck_controlled_result_review_state",
        ),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["reviewed_by"], ["users.id"], ondelete="RESTRICT"),
    )
    for column in ("organization_id", "project_id", "document_id", "created_by"):
        op.create_index(f"ix_controlled_result_records_{column}", "controlled_result_records", [column])

    op.create_table(
        "result_feedback",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("result_id", sa.String(36), nullable=False),
        sa.Column("project_id", sa.String(36), nullable=False),
        sa.Column("result_version", sa.String(64), nullable=False),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("created_by", sa.String(36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("rating >= 1 AND rating <= 5", name="ck_result_feedback_rating"),
        sa.UniqueConstraint("result_id", "created_by", name="uq_result_feedback_result_user"),
        sa.ForeignKeyConstraint(
            ["result_id"], ["controlled_result_records.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="CASCADE"),
    )
    for column in ("result_id", "project_id", "created_by"):
        op.create_index(f"ix_result_feedback_{column}", "result_feedback", [column])


def downgrade() -> None:
    for column in ("created_by", "project_id", "result_id"):
        op.drop_index(f"ix_result_feedback_{column}", table_name="result_feedback")
    op.drop_table("result_feedback")
    for column in ("created_by", "document_id", "project_id", "organization_id"):
        op.drop_index(
            f"ix_controlled_result_records_{column}", table_name="controlled_result_records"
        )
    op.drop_table("controlled_result_records")
