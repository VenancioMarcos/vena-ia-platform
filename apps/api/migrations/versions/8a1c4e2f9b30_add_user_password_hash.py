"""add user password hash

Revision ID: 8a1c4e2f9b30
Revises: 4c3d8f1a2b7e
Create Date: 2026-07-29
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "8a1c4e2f9b30"
down_revision: str | None = "4c3d8f1a2b7e"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("password_hash", sa.String(length=512), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("users", "password_hash")
