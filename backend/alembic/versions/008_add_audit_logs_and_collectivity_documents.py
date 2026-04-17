"""add audit_logs and collectivity_documents tables

Revision ID: 008
Revises: 007
Create Date: 2026-04-17 02:30:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "008"
down_revision: str | None = "007"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "audit_logs",
        sa.Column(
            "id",
            sa.Uuid(),
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("actor_user_id", sa.Uuid(), nullable=False),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("target_type", sa.String(100), nullable=False),
        sa.Column("target_id", sa.Uuid(), nullable=False),
        sa.Column(
            "payload",
            sa.dialects.postgresql.JSONB(),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["actor_user_id"], ["users.id"], ondelete="RESTRICT"
        ),
    )
    op.create_index(
        "ix_audit_logs_action_created",
        "audit_logs",
        ["action", sa.text("created_at DESC")],
    )
    op.create_index(
        "ix_audit_logs_actor_created",
        "audit_logs",
        ["actor_user_id", sa.text("created_at DESC")],
    )

    op.create_table(
        "collectivity_documents",
        sa.Column(
            "id",
            sa.Uuid(),
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("province_id", sa.Uuid(), nullable=True),
        sa.Column("region_id", sa.Uuid(), nullable=True),
        sa.Column("commune_id", sa.Uuid(), nullable=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("file_path", sa.String(500), nullable=False),
        sa.Column("file_mime", sa.String(127), nullable=False),
        sa.Column("file_size_bytes", sa.BigInteger(), nullable=False),
        sa.Column(
            "position", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["province_id"], ["provinces.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["region_id"], ["regions.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["commune_id"], ["communes.id"], ondelete="CASCADE"
        ),
        sa.CheckConstraint(
            "((province_id IS NOT NULL)::int + (region_id IS NOT NULL)::int "
            "+ (commune_id IS NOT NULL)::int) = 1",
            name="ck_collectivity_documents_parent_exclusive",
        ),
    )
    op.create_index(
        "ix_collectivity_documents_province_position",
        "collectivity_documents",
        ["province_id", "position"],
        postgresql_where=sa.text("province_id IS NOT NULL"),
    )
    op.create_index(
        "ix_collectivity_documents_region_position",
        "collectivity_documents",
        ["region_id", "position"],
        postgresql_where=sa.text("region_id IS NOT NULL"),
    )
    op.create_index(
        "ix_collectivity_documents_commune_position",
        "collectivity_documents",
        ["commune_id", "position"],
        postgresql_where=sa.text("commune_id IS NOT NULL"),
    )


def downgrade() -> None:
    op.drop_index(
        "ix_collectivity_documents_commune_position",
        table_name="collectivity_documents",
    )
    op.drop_index(
        "ix_collectivity_documents_region_position",
        table_name="collectivity_documents",
    )
    op.drop_index(
        "ix_collectivity_documents_province_position",
        table_name="collectivity_documents",
    )
    op.drop_table("collectivity_documents")

    op.drop_index("ix_audit_logs_actor_created", table_name="audit_logs")
    op.drop_index("ix_audit_logs_action_created", table_name="audit_logs")
    op.drop_table("audit_logs")
