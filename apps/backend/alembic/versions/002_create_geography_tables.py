"""create_geography_tables

Revision ID: 002
Revises: 001
Create Date: 2026-03-20 20:00:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "002"
down_revision: str | Sequence[str] | None = "001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "provinces",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("code", sa.String(20), nullable=False),
        sa.Column("description_json", JSONB, nullable=False, server_default="[]"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_provinces_code", "provinces", ["code"], unique=True)

    op.create_table(
        "regions",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("code", sa.String(20), nullable=False),
        sa.Column(
            "province_id",
            sa.Uuid(),
            sa.ForeignKey("provinces.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("description_json", JSONB, nullable=False, server_default="[]"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_regions_code", "regions", ["code"], unique=True)
    op.create_index("ix_regions_province_id", "regions", ["province_id"])

    op.create_table(
        "communes",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("code", sa.String(20), nullable=False),
        sa.Column(
            "region_id",
            sa.Uuid(),
            sa.ForeignKey("regions.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("description_json", JSONB, nullable=False, server_default="[]"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_communes_code", "communes", ["code"], unique=True)
    op.create_index("ix_communes_region_id", "communes", ["region_id"])


def downgrade() -> None:
    op.drop_index("ix_communes_region_id", table_name="communes")
    op.drop_index("ix_communes_code", table_name="communes")
    op.drop_table("communes")
    op.drop_index("ix_regions_province_id", table_name="regions")
    op.drop_index("ix_regions_code", table_name="regions")
    op.drop_table("regions")
    op.drop_index("ix_provinces_code", table_name="provinces")
    op.drop_table("provinces")
