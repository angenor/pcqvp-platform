"""create editorial_contents, contact_info, resource_links tables

Revision ID: 006
Revises: 005
Create Date: 2026-03-28 10:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "006"
down_revision: str | None = "005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Editorial contents (hero, body, footer about)
    op.create_table(
        "editorial_contents",
        sa.Column(
            "id",
            sa.Uuid(),
            nullable=False,
            default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("section_key", sa.String(50), nullable=False),
        sa.Column("content_text", sa.Text(), nullable=True),
        sa.Column(
            "content_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column("updated_by", sa.Uuid(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("section_key"),
        sa.ForeignKeyConstraint(
            ["updated_by"], ["users.id"], ondelete="SET NULL"
        ),
    )

    # Contact info (singleton)
    op.create_table(
        "contact_info",
        sa.Column(
            "id",
            sa.Uuid(),
            nullable=False,
            default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("phone", sa.String(50), nullable=True),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("updated_by", sa.Uuid(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["updated_by"], ["users.id"], ondelete="SET NULL"
        ),
    )

    # Resource links (ordered list)
    op.create_table(
        "resource_links",
        sa.Column(
            "id",
            sa.Uuid(),
            nullable=False,
            default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("url", sa.String(500), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_resource_links_sort_order",
        "resource_links",
        ["sort_order"],
    )


def downgrade() -> None:
    op.drop_index("ix_resource_links_sort_order", table_name="resource_links")
    op.drop_table("resource_links")
    op.drop_table("contact_info")
    op.drop_table("editorial_contents")
