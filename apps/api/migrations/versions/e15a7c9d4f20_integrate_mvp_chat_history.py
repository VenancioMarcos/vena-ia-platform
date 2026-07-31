"""integrate MVP grounded chat history

Revision ID: e15a7c9d4f20
Revises: d04f6b8a3c19
Create Date: 2026-07-30
"""

import sqlalchemy as sa
from alembic import op

revision = "e15a7c9d4f20"
down_revision = "d04f6b8a3c19"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "messages",
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=True),
    )
    op.add_column(
        "messages",
        sa.Column(
            "status",
            sa.String(20),
            nullable=False,
            server_default="COMPLETED",
        ),
    )
    op.add_column(
        "messages",
        sa.Column(
            "evidence",
            sa.JSON(),
            nullable=False,
            server_default=sa.text("'[]'::json"),
        ),
    )
    op.add_column("messages", sa.Column("error", sa.String(255), nullable=True))
    op.create_index("ix_messages_user_id", "messages", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_messages_user_id", table_name="messages")
    op.drop_column("messages", "error")
    op.drop_column("messages", "evidence")
    op.drop_column("messages", "status")
    op.drop_column("messages", "user_id")
