"""
Script de migration : ancien format description_json (liste de blocs) → format EditorJS.

Usage:
    cd apps/backend
    python scripts/migrate_description_format.py
"""

import asyncio
import time
import uuid

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import get_settings

settings = get_settings()


def convert_block(block: dict) -> dict:
    """Convertit un bloc ancien format vers EditorJS."""
    old_type = block.get("type", "")
    if old_type == "heading":
        return {
            "id": str(uuid.uuid4())[:10],
            "type": "header",
            "data": {"text": block.get("content", ""), "level": 2},
        }
    elif old_type == "paragraph":
        return {
            "id": str(uuid.uuid4())[:10],
            "type": "paragraph",
            "data": {"text": block.get("content", "")},
        }
    elif old_type == "image":
        return {
            "id": str(uuid.uuid4())[:10],
            "type": "image",
            "data": {
                "file": {"url": block.get("url", "")},
                "caption": block.get("alt", ""),
            },
        }
    else:
        return {
            "id": str(uuid.uuid4())[:10],
            "type": "paragraph",
            "data": {"text": str(block.get("content", ""))},
        }


def convert_description(old_data) -> dict | None:
    """Convertit description_json ancien format vers EditorJS."""
    if old_data is None:
        return None
    if isinstance(old_data, dict) and "blocks" in old_data:
        return old_data  # Already in EditorJS format
    if isinstance(old_data, list):
        if not old_data:
            return None
        blocks = [convert_block(b) for b in old_data]
        return {
            "time": int(time.time() * 1000),
            "blocks": blocks,
            "version": "2.31.0",
        }
    return None


async def migrate():
    engine = create_async_engine(settings.DATABASE_URL)
    tables = ["provinces", "regions", "communes"]

    async with engine.begin() as conn:
        for table in tables:
            rows = await conn.execute(
                text(f"SELECT id, description_json FROM {table} WHERE description_json IS NOT NULL")
            )
            count = 0
            for row in rows:
                row_id, old_data = row
                new_data = convert_description(old_data)
                if new_data != old_data:
                    await conn.execute(
                        text(f"UPDATE {table} SET description_json = :data WHERE id = :id"),
                        {"data": str(new_data).replace("'", '"') if new_data else None, "id": row_id},
                    )
                    count += 1
            print(f"  {table}: {count} row(s) migrated")

    await engine.dispose()
    print("Migration complete.")


if __name__ == "__main__":
    asyncio.run(migrate())
