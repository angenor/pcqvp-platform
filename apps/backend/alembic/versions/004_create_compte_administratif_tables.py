"""create_compte_administratif_tables

Revision ID: 004
Revises: 003
Create Date: 2026-03-21 10:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "004"
down_revision: str | None = "003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("""
        DO $$ BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'collectivitetype') THEN
                CREATE TYPE collectivitetype AS ENUM ('province', 'region', 'commune');
            END IF;
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'comptestatus') THEN
                CREATE TYPE comptestatus AS ENUM ('draft', 'published');
            END IF;
        END $$;
    """)

    op.execute("""
        CREATE TABLE comptes_administratifs (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            collectivite_type collectivitetype NOT NULL,
            collectivite_id UUID NOT NULL,
            annee_exercice INTEGER NOT NULL,
            status comptestatus NOT NULL DEFAULT 'draft',
            created_by UUID NOT NULL REFERENCES users(id),
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ,
            CONSTRAINT uq_compte_collectivite_annee UNIQUE (collectivite_type, collectivite_id, annee_exercice)
        )
    """)
    op.create_index(
        "ix_comptes_collectivite",
        "comptes_administratifs",
        ["collectivite_type", "collectivite_id"],
    )
    op.create_index(
        "ix_comptes_annee", "comptes_administratifs", ["annee_exercice"]
    )

    op.create_table(
        "recette_lines",
        sa.Column("id", sa.Uuid(), nullable=False, default=sa.text("gen_random_uuid()")),
        sa.Column("compte_admin_id", sa.Uuid(), nullable=False),
        sa.Column("template_line_id", sa.Uuid(), nullable=False),
        sa.Column(
            "values",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="{}",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["compte_admin_id"],
            ["comptes_administratifs.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["template_line_id"],
            ["account_template_lines.id"],
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint(
            "compte_admin_id",
            "template_line_id",
            name="uq_recette_compte_template",
        ),
    )

    op.create_table(
        "depense_programs",
        sa.Column("id", sa.Uuid(), nullable=False, default=sa.text("gen_random_uuid()")),
        sa.Column("compte_admin_id", sa.Uuid(), nullable=False),
        sa.Column("numero", sa.Integer(), nullable=False),
        sa.Column("intitule", sa.String(255), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["compte_admin_id"],
            ["comptes_administratifs.id"],
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint(
            "compte_admin_id", "numero", name="uq_programme_compte_numero"
        ),
    )

    op.create_table(
        "depense_lines",
        sa.Column("id", sa.Uuid(), nullable=False, default=sa.text("gen_random_uuid()")),
        sa.Column("programme_id", sa.Uuid(), nullable=False),
        sa.Column("template_line_id", sa.Uuid(), nullable=False),
        sa.Column(
            "values",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="{}",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["programme_id"],
            ["depense_programs.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["template_line_id"],
            ["account_template_lines.id"],
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint(
            "programme_id",
            "template_line_id",
            name="uq_depense_programme_template",
        ),
    )

    op.create_table(
        "account_change_logs",
        sa.Column("id", sa.Uuid(), nullable=False, default=sa.text("gen_random_uuid()")),
        sa.Column("compte_admin_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("change_type", sa.String(50), nullable=False),
        sa.Column(
            "detail",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["compte_admin_id"],
            ["comptes_administratifs.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
    )
    op.create_index(
        "ix_changelog_compte_date",
        "account_change_logs",
        ["compte_admin_id", "created_at"],
    )


def downgrade() -> None:
    op.drop_table("account_change_logs")
    op.drop_table("depense_lines")
    op.drop_table("depense_programs")
    op.drop_table("recette_lines")
    op.drop_table("comptes_administratifs")
    op.execute("DROP TYPE IF EXISTS comptestatus")
    op.execute("DROP TYPE IF EXISTS collectivitetype")
