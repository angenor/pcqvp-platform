"""create_account_template_tables

Revision ID: 003
Revises: 002
Create Date: 2026-03-20 22:00:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "003"
down_revision: str | Sequence[str] | None = "002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    templatetype = sa.Enum(
        "recette", "depense", name="templatetype", create_type=True
    )
    sectiontype = sa.Enum(
        "fonctionnement", "investissement", name="sectiontype", create_type=True
    )
    columndatatype = sa.Enum(
        "number", "text", "percentage", name="columndatatype", create_type=True
    )

    op.create_table(
        "account_templates",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("type", templatetype, nullable=False),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("name", "version", name="uq_template_name_version"),
    )
    op.create_index(
        "ix_account_templates_type", "account_templates", ["type"]
    )

    op.create_table(
        "account_template_lines",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "template_id",
            sa.Uuid(),
            sa.ForeignKey("account_templates.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("compte_code", sa.String(10), nullable=False),
        sa.Column("intitule", sa.String(500), nullable=False),
        sa.Column("level", sa.Integer(), nullable=False),
        sa.Column("parent_code", sa.String(10), nullable=True),
        sa.Column("section", sectiontype, nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.UniqueConstraint(
            "template_id", "compte_code", name="uq_line_template_code"
        ),
        sa.CheckConstraint("level IN (1, 2, 3)", name="ck_line_level"),
    )
    op.create_index(
        "ix_lines_template_level",
        "account_template_lines",
        ["template_id", "level"],
    )
    op.create_index(
        "ix_lines_template_parent",
        "account_template_lines",
        ["template_id", "parent_code"],
    )
    op.create_index(
        "ix_lines_template_section",
        "account_template_lines",
        ["template_id", "section"],
    )

    op.create_table(
        "account_template_columns",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "template_id",
            sa.Uuid(),
            sa.ForeignKey("account_templates.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("code", sa.String(50), nullable=False),
        sa.Column("data_type", columndatatype, nullable=False),
        sa.Column(
            "is_computed",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column("formula", sa.String(500), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.UniqueConstraint(
            "template_id", "code", name="uq_column_template_code"
        ),
    )
    op.create_index(
        "ix_columns_template_id",
        "account_template_columns",
        ["template_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_columns_template_id", table_name="account_template_columns")
    op.drop_table("account_template_columns")
    op.drop_index(
        "ix_lines_template_section", table_name="account_template_lines"
    )
    op.drop_index(
        "ix_lines_template_parent", table_name="account_template_lines"
    )
    op.drop_index(
        "ix_lines_template_level", table_name="account_template_lines"
    )
    op.drop_table("account_template_lines")
    op.drop_index("ix_account_templates_type", table_name="account_templates")
    op.drop_table("account_templates")

    sa.Enum(name="columndatatype").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="sectiontype").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="templatetype").drop(op.get_bind(), checkfirst=True)
