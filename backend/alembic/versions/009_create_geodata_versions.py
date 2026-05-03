"""create geodata_versions table

Revision ID: 009
Revises: 008
Create Date: 2026-05-03 12:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "009"
down_revision: str | None = "008"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "geodata_versions",
        sa.Column(
            "id",
            sa.Uuid(),
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("created_by_user_id", sa.Uuid(), nullable=False),
        sa.Column("original_filename", sa.String(255), nullable=False),
        sa.Column("original_size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("processed_size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("features_count", sa.Integer(), nullable=False),
        sa.Column(
            "region_names",
            sa.dialects.postgresql.JSONB(),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column(
            "geojson_processed",
            sa.dialects.postgresql.JSONB(),
            nullable=False,
        ),
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "warnings",
            sa.dialects.postgresql.JSONB(),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["created_by_user_id"], ["users.id"], ondelete="RESTRICT"
        ),
    )
    op.create_index(
        "uq_geodata_version_one_active",
        "geodata_versions",
        ["is_active"],
        unique=True,
        postgresql_where=sa.text("is_active IS TRUE"),
    )
    op.create_index(
        "ix_geodata_versions_active_lookup",
        "geodata_versions",
        ["is_active"],
        postgresql_where=sa.text("is_active IS TRUE"),
    )
    op.create_index(
        "ix_geodata_versions_created_at",
        "geodata_versions",
        [sa.text("created_at DESC")],
    )
    op.create_index(
        "ix_geodata_versions_created_by",
        "geodata_versions",
        ["created_by_user_id", sa.text("created_at DESC")],
    )


def downgrade() -> None:
    op.drop_index("ix_geodata_versions_created_by", table_name="geodata_versions")
    op.drop_index("ix_geodata_versions_created_at", table_name="geodata_versions")
    op.drop_index(
        "ix_geodata_versions_active_lookup", table_name="geodata_versions"
    )
    op.drop_index("uq_geodata_version_one_active", table_name="geodata_versions")
    op.drop_table("geodata_versions")
