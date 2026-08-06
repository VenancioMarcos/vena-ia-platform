"""add versioned engineering catalog

Revision ID: c27f6d9e4a10
Revises: b18e4c7d2a91
Create Date: 2026-08-06
"""

import sqlalchemy as sa
from alembic import op

revision = "c27f6d9e4a10"
down_revision = "b18e4c7d2a91"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "engineering_catalog_items",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("kind", sa.String(32), nullable=False),
        sa.Column("code", sa.String(100), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("data_version", sa.String(64), nullable=False),
        sa.Column("source", sa.Text(), nullable=False),
        sa.Column("properties", sa.JSON(), nullable=False),
        sa.Column("created_by", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("kind", "code", "data_version", name="uq_engineering_catalog_version"),
    )
    op.create_index("ix_engineering_catalog_items_kind", "engineering_catalog_items", ["kind"])
    op.create_index("ix_engineering_catalog_items_code", "engineering_catalog_items", ["code"])
    op.create_index(
        "ix_engineering_catalog_items_created_by", "engineering_catalog_items", ["created_by"]
    )


def downgrade() -> None:
    op.drop_table("engineering_catalog_items")
