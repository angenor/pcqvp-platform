"""seed initial geodata version (Madagascar regions v1)

Revision ID: 010
Revises: 009
Create Date: 2026-05-03 12:05:00.000000

"""

import json
from collections.abc import Sequence
from pathlib import Path

import sqlalchemy as sa

from alembic import op

revision: str = "010"
down_revision: str | None = "009"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

SEED_FILENAME = "madagascar_regions_v1.geojson"
SEED_PATH = Path(__file__).resolve().parents[1] / "seed" / SEED_FILENAME


def _load_seed() -> dict:
    with SEED_PATH.open(encoding="utf-8") as fh:
        return json.load(fh)


def _resolve_admin_user_id(connection) -> str:
    row = connection.execute(
        sa.text(
            "SELECT id FROM users WHERE role = 'admin' "
            "ORDER BY created_at ASC LIMIT 1"
        )
    ).first()
    if row is None:
        raise RuntimeError(
            "No admin user found. Run scripts/seed_admin.py before applying "
            "migration 010."
        )
    return str(row[0])


def upgrade() -> None:
    connection = op.get_bind()
    geojson = _load_seed()
    features = geojson.get("features", [])
    region_names = [f["properties"]["name"] for f in features]
    payload = json.dumps(geojson, ensure_ascii=False, separators=(",", ":"))
    processed_size = len(payload.encode("utf-8"))
    original_size = SEED_PATH.stat().st_size
    user_id = _resolve_admin_user_id(connection)

    connection.execute(
        sa.text(
            """
            INSERT INTO geodata_versions (
                id, created_at, created_by_user_id, original_filename,
                original_size_bytes, processed_size_bytes, features_count,
                region_names, geojson_processed, is_active, notes, warnings
            ) VALUES (
                gen_random_uuid(), now(), :user_id, :fname,
                :osize, :psize, :fcount,
                CAST(:rnames AS jsonb), CAST(:gj AS jsonb), TRUE, :notes,
                CAST(:warns AS jsonb)
            )
            """
        ),
        {
            "user_id": user_id,
            "fname": SEED_FILENAME,
            "osize": original_size,
            "psize": processed_size,
            "fcount": len(features),
            "rnames": json.dumps(region_names, ensure_ascii=False),
            "gj": payload,
            "notes": "Seed initial — 23 régions de Madagascar (v1).",
            "warns": "[]",
        },
    )


def downgrade() -> None:
    op.execute(
        f"DELETE FROM geodata_versions WHERE original_filename = '{SEED_FILENAME}'"
    )
