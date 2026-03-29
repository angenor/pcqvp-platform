"""add banner_image to provinces, regions, communes

Revision ID: 007
Revises: 006
Create Date: 2026-03-28 14:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "007"
down_revision: str | None = "006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "provinces", sa.Column("banner_image", sa.String(500), nullable=True)
    )
    op.add_column(
        "regions", sa.Column("banner_image", sa.String(500), nullable=True)
    )
    op.add_column(
        "communes", sa.Column("banner_image", sa.String(500), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("communes", "banner_image")
    op.drop_column("regions", "banner_image")
    op.drop_column("provinces", "banner_image")
