"""add cross-cutting features: newsletter, visit_logs, site_configurations, search_vectors

Revision ID: 005
Revises: 004
Create Date: 2026-03-21 12:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "005"
down_revision: str | None = "004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. Create unaccent extension
    op.execute("CREATE EXTENSION IF NOT EXISTS unaccent")

    # 2. Create fr_unaccent text search configuration
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_ts_config WHERE cfgname = 'fr_unaccent'
            ) THEN
                CREATE TEXT SEARCH CONFIGURATION fr_unaccent (COPY = french);
                ALTER TEXT SEARCH CONFIGURATION fr_unaccent
                    ALTER MAPPING FOR hword, hword_part, word
                    WITH unaccent, french_stem;
            END IF;
        END
        $$;
    """)

    # 3. Create newsletter_subscribers table
    op.create_table(
        "newsletter_subscribers",
        sa.Column("id", sa.Uuid(), nullable=False, default=sa.text("gen_random_uuid()")),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="en_attente"),
        sa.Column("unsubscribe_token", sa.String(255), nullable=False),
        sa.Column("confirmed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("unsubscribed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("unsubscribe_token"),
    )
    op.create_index("ix_newsletter_subscribers_email", "newsletter_subscribers", ["email"])
    op.create_index("ix_newsletter_subscribers_status", "newsletter_subscribers", ["status"])

    # 4. Create visit_logs table
    op.create_table(
        "visit_logs",
        sa.Column("id", sa.Uuid(), nullable=False, default=sa.text("gen_random_uuid()")),
        sa.Column("event_type", sa.String(20), nullable=False),
        sa.Column("path", sa.String(500), nullable=False),
        sa.Column("page_type", sa.String(50), nullable=True),
        sa.Column("collectivite_type", sa.String(20), nullable=True),
        sa.Column("collectivite_id", sa.Uuid(), nullable=True),
        sa.Column("download_format", sa.String(10), nullable=True),
        sa.Column("user_agent", sa.String(500), nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_visit_logs_created_at", "visit_logs", ["created_at"])
    op.create_index("ix_visit_logs_event_type", "visit_logs", ["event_type"])
    op.create_index("ix_visit_logs_page_type", "visit_logs", ["page_type"])

    # 5. Create site_configurations table
    op.create_table(
        "site_configurations",
        sa.Column("id", sa.Uuid(), nullable=False, default=sa.text("gen_random_uuid()")),
        sa.Column("key", sa.String(100), nullable=False),
        sa.Column("value", sa.Text(), nullable=False, server_default=""),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("key"),
    )

    # 6. Seed globalleaks_url config
    op.execute("""
        INSERT INTO site_configurations (id, key, value, created_at)
        VALUES (gen_random_uuid(), 'globalleaks_url', '', now())
    """)

    # 7. Add search_vector columns on geography tables
    for table in ("provinces", "regions", "communes"):
        op.execute(f"""
            ALTER TABLE {table}
            ADD COLUMN search_vector tsvector
            GENERATED ALWAYS AS (to_tsvector('fr_unaccent', coalesce(name, ''))) STORED
        """)
        op.create_index(
            f"ix_{table}_search_vector",
            table,
            ["search_vector"],
            postgresql_using="gin",
        )


def downgrade() -> None:
    # Remove search_vector columns and indexes
    for table in ("communes", "regions", "provinces"):
        op.drop_index(f"ix_{table}_search_vector", table_name=table)
        op.drop_column(table, "search_vector")

    # Drop tables
    op.drop_table("site_configurations")
    op.drop_index("ix_visit_logs_page_type", table_name="visit_logs")
    op.drop_index("ix_visit_logs_event_type", table_name="visit_logs")
    op.drop_index("ix_visit_logs_created_at", table_name="visit_logs")
    op.drop_table("visit_logs")
    op.drop_index("ix_newsletter_subscribers_status", table_name="newsletter_subscribers")
    op.drop_index("ix_newsletter_subscribers_email", table_name="newsletter_subscribers")
    op.drop_table("newsletter_subscribers")

    # Drop text search config and extension
    op.execute("DROP TEXT SEARCH CONFIGURATION IF EXISTS fr_unaccent")
    op.execute("DROP EXTENSION IF EXISTS unaccent")
