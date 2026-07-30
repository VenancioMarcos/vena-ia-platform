"""add document chunks

Revision ID: b7f3c9d2e614
Revises: 8a1c4e2f9b30
Create Date: 2026-07-30

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "b7f3c9d2e614"
down_revision = "8a1c4e2f9b30"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "document_chunks",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column(
            "document_id",
            sa.String(length=36),
            sa.ForeignKey("documents.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("page_number", sa.Integer(), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("start_offset", sa.Integer(), nullable=False),
        sa.Column("end_offset", sa.Integer(), nullable=False),
        sa.Column("character_count", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint(
            "page_number >= 1",
            name="ck_document_chunks_page_number",
        ),
        sa.CheckConstraint(
            "chunk_index >= 0",
            name="ck_document_chunks_chunk_index",
        ),
        sa.CheckConstraint(
            "start_offset >= 0",
            name="ck_document_chunks_start_offset",
        ),
        sa.CheckConstraint(
            "end_offset > start_offset",
            name="ck_document_chunks_end_offset",
        ),
        sa.CheckConstraint(
            "character_count > 0",
            name="ck_document_chunks_character_count",
        ),
        sa.UniqueConstraint(
            "document_id",
            "chunk_index",
            name="uq_document_chunks_document_chunk_index",
        ),
    )
    op.create_index(
        "ix_document_chunks_document_id",
        "document_chunks",
        ["document_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_document_chunks_document_id",
        table_name="document_chunks",
    )
    op.drop_table("document_chunks")
