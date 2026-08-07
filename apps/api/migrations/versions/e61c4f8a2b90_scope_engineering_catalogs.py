"""scope engineering catalogs by organization

Revision ID: e61c4f8a2b90
Revises: d39a7b2c5e11
Create Date: 2026-08-07
"""

import sqlalchemy as sa
from alembic import op

revision = "e61c4f8a2b90"
down_revision = "d39a7b2c5e11"
branch_labels = None
depends_on = None


def _drop_legacy_unique_if_present() -> None:
    inspector = sa.inspect(op.get_bind())
    names = {
        constraint["name"]
        for constraint in inspector.get_unique_constraints("engineering_catalog_items")
    }
    if "uq_engineering_catalog_version" in names:
        op.drop_constraint(
            "uq_engineering_catalog_version",
            "engineering_catalog_items",
            type_="unique",
        )


def upgrade() -> None:
    op.add_column(
        "engineering_catalog_items",
        sa.Column(
            "scope_type",
            sa.String(32),
            nullable=False,
            server_default="LEGACY_UNSCOPED",
        ),
    )
    op.add_column(
        "engineering_catalog_items",
        sa.Column(
            "organization_id",
            sa.String(36),
            sa.ForeignKey("organizations.id", ondelete="RESTRICT"),
            nullable=True,
        ),
    )
    _drop_legacy_unique_if_present()
    op.create_check_constraint(
        "ck_engineering_catalog_scope_type",
        "engineering_catalog_items",
        "scope_type IN ('SYSTEM_REFERENCE', 'ORGANIZATION_OWNED', 'LEGACY_UNSCOPED')",
    )
    op.create_check_constraint(
        "ck_engineering_catalog_scope_owner",
        "engineering_catalog_items",
        "(scope_type = 'ORGANIZATION_OWNED' AND organization_id IS NOT NULL) OR "
        "(scope_type != 'ORGANIZATION_OWNED' AND organization_id IS NULL)",
    )
    op.create_index(
        "ix_engineering_catalog_items_scope_type",
        "engineering_catalog_items",
        ["scope_type"],
    )
    op.create_index(
        "ix_engineering_catalog_items_organization_id",
        "engineering_catalog_items",
        ["organization_id"],
    )
    op.create_index(
        "uq_engineering_catalog_organization_version",
        "engineering_catalog_items",
        ["organization_id", "kind", "code", "data_version"],
        unique=True,
        postgresql_where=sa.text("scope_type = 'ORGANIZATION_OWNED'"),
        sqlite_where=sa.text("scope_type = 'ORGANIZATION_OWNED'"),
    )
    op.create_index(
        "uq_engineering_catalog_system_version",
        "engineering_catalog_items",
        ["kind", "code", "data_version"],
        unique=True,
        postgresql_where=sa.text("scope_type = 'SYSTEM_REFERENCE'"),
        sqlite_where=sa.text("scope_type = 'SYSTEM_REFERENCE'"),
    )


def downgrade() -> None:
    op.drop_index(
        "uq_engineering_catalog_system_version", table_name="engineering_catalog_items"
    )
    op.drop_index(
        "uq_engineering_catalog_organization_version", table_name="engineering_catalog_items"
    )
    op.drop_index(
        "ix_engineering_catalog_items_organization_id", table_name="engineering_catalog_items"
    )
    op.drop_index(
        "ix_engineering_catalog_items_scope_type", table_name="engineering_catalog_items"
    )
    op.drop_constraint(
        "ck_engineering_catalog_scope_owner",
        "engineering_catalog_items",
        type_="check",
    )
    op.drop_constraint(
        "ck_engineering_catalog_scope_type",
        "engineering_catalog_items",
        type_="check",
    )
    op.drop_column("engineering_catalog_items", "organization_id")
    op.drop_column("engineering_catalog_items", "scope_type")
    # The former global uniqueness constraint is intentionally not restored: scoped
    # organizations may validly contain the same catalog version, and downgrade must
    # preserve those rows without inventing ownership or deleting data.
