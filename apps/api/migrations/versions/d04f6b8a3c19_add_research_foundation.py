"""add scientific research foundation

Revision ID: d04f6b8a3c19
Revises: c91e5a4f2d08
Create Date: 2026-07-30
"""

import sqlalchemy as sa
from alembic import op

revision = "d04f6b8a3c19"
down_revision = "c91e5a4f2d08"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "research_articles",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "project_id",
            sa.String(36),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "document_id",
            sa.String(36),
            sa.ForeignKey("documents.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("created_by", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("title", sa.String(500)),
        sa.Column("authors", sa.JSON(), nullable=False),
        sa.Column("year", sa.Integer()),
        sa.Column("venue", sa.String(500)),
        sa.Column("volume", sa.String(50)),
        sa.Column("issue", sa.String(50)),
        sa.Column("pages", sa.String(100)),
        sa.Column("doi", sa.String(255)),
        sa.Column("keywords", sa.JSON(), nullable=False),
        sa.Column("abstract", sa.Text()),
        sa.Column("document_type", sa.String(50), nullable=False),
        sa.Column("language", sa.String(20)),
        sa.Column("metadata_status", sa.String(50), nullable=False),
        sa.Column("metadata_source", sa.String(50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("document_id", name="uq_research_articles_document_id"),
    )
    op.create_index("ix_research_articles_project_id", "research_articles", ["project_id"])
    op.create_index(
        "ix_research_articles_document_id", "research_articles", ["document_id"]
    )
    op.create_table(
        "research_references",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "article_id",
            sa.String(36),
            sa.ForeignKey("research_articles.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("raw_text", sa.Text(), nullable=False),
        sa.Column("authors", sa.Text()),
        sa.Column("title", sa.String(500)),
        sa.Column("year", sa.Integer()),
        sa.Column("venue", sa.String(500)),
        sa.Column("doi", sa.String(255)),
        sa.Column("page_number", sa.Integer(), nullable=False),
        sa.Column("extraction_method", sa.String(50), nullable=False),
        sa.Column("status", sa.String(50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_research_references_article_id", "research_references", ["article_id"]
    )
    op.create_table(
        "doe_studies",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "project_id",
            sa.String(36),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("created_by", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("objective", sa.Text(), nullable=False),
        sa.Column("response_variables", sa.JSON(), nullable=False),
        sa.Column("factors", sa.JSON(), nullable=False),
        sa.Column("design_type", sa.String(50), nullable=False),
        sa.Column("repetitions", sa.Integer(), nullable=False),
        sa.Column("randomization_required", sa.Boolean(), nullable=False),
        sa.Column("blocking_notes", sa.Text()),
        sa.Column("assumptions", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(80), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_doe_studies_project_id", "doe_studies", ["project_id"])
    op.create_table(
        "anova_datasets",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "project_id",
            sa.String(36),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("created_by", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("factor_name", sa.String(255), nullable=False),
        sa.Column("response_name", sa.String(255), nullable=False),
        sa.Column("response_unit", sa.String(100), nullable=False),
        sa.Column("observations", sa.JSON(), nullable=False),
        sa.Column("descriptive_summary", sa.JSON(), nullable=False),
        sa.Column("assumptions_checklist", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(80), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_anova_datasets_project_id", "anova_datasets", ["project_id"])
    op.create_table(
        "research_reports",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "project_id",
            sa.String(36),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("created_by", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("report_type", sa.String(50), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("objective", sa.Text(), nullable=False),
        sa.Column("document_ids", sa.JSON(), nullable=False),
        sa.Column("synthesis", sa.Text(), nullable=False),
        sa.Column("evidence", sa.JSON(), nullable=False),
        sa.Column("limitations", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_research_reports_project_id", "research_reports", ["project_id"])


def downgrade() -> None:
    op.drop_index("ix_research_reports_project_id", table_name="research_reports")
    op.drop_table("research_reports")
    op.drop_index("ix_anova_datasets_project_id", table_name="anova_datasets")
    op.drop_table("anova_datasets")
    op.drop_index("ix_doe_studies_project_id", table_name="doe_studies")
    op.drop_table("doe_studies")
    op.drop_index("ix_research_references_article_id", table_name="research_references")
    op.drop_table("research_references")
    op.drop_index("ix_research_articles_document_id", table_name="research_articles")
    op.drop_index("ix_research_articles_project_id", table_name="research_articles")
    op.drop_table("research_articles")
