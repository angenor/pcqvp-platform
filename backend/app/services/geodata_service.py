"""Orchestration DB pour les versions geodata."""

from __future__ import annotations

import unicodedata
import uuid

from fastapi import HTTPException, status
from sqlalchemy import func, select, text, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.geodata_version import GeodataVersion
from app.models.user import User
from app.services.geodata_pipeline import PipelineResult


def _norm(s: str) -> str:
    n = unicodedata.normalize("NFD", s)
    return "".join(c for c in n if unicodedata.category(c) != "Mn").lower().strip()


async def create_version(
    db: AsyncSession,
    user: User,
    pipeline_result: PipelineResult,
    *,
    original_filename: str,
    original_size: int,
    notes: str | None,
    max_versions: int,
) -> GeodataVersion:
    """Crée une nouvelle version (inactive) ; purge LRU si quota atteint."""
    await _purge_lru_inactive_locked(db, max_versions=max_versions)
    version = GeodataVersion(
        created_by_user_id=user.id,
        original_filename=original_filename,
        original_size_bytes=original_size,
        processed_size_bytes=pipeline_result.processed_size_bytes,
        features_count=len(pipeline_result.features),
        region_names=list(pipeline_result.region_names),
        geojson_processed=pipeline_result.geojson,
        is_active=False,
        notes=notes,
        warnings=list(pipeline_result.warnings),
    )
    db.add(version)
    await db.flush()
    await db.refresh(version)
    return version


async def _purge_lru_inactive_locked(
    db: AsyncSession, *, max_versions: int
) -> None:
    count_stmt = select(func.count()).select_from(GeodataVersion)
    total = (await db.execute(count_stmt)).scalar_one()
    if total < max_versions:
        return
    to_remove = total - max_versions + 1
    stmt = (
        select(GeodataVersion)
        .where(GeodataVersion.is_active.is_(False))
        .order_by(GeodataVersion.created_at.asc())
        .limit(to_remove)
    )
    rows = (await db.execute(stmt)).scalars().all()
    for v in rows:
        await db.delete(v)
    await db.flush()


async def list_versions(
    db: AsyncSession, *, limit: int, offset: int
) -> tuple[list[GeodataVersion], int]:
    total = (
        await db.execute(select(func.count()).select_from(GeodataVersion))
    ).scalar_one()
    stmt = (
        select(GeodataVersion)
        .order_by(GeodataVersion.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    items = (await db.execute(stmt)).scalars().all()
    return list(items), int(total)


async def get_version(
    db: AsyncSession, version_id: uuid.UUID
) -> GeodataVersion | None:
    return await db.get(GeodataVersion, version_id)


async def get_active_version(db: AsyncSession) -> GeodataVersion | None:
    stmt = (
        select(GeodataVersion)
        .where(GeodataVersion.is_active.is_(True))
        .limit(1)
    )
    return (await db.execute(stmt)).scalar_one_or_none()


async def activate_version(
    db: AsyncSession, target_id: uuid.UUID
) -> GeodataVersion:
    """Active la version cible et désactive l'actuelle, atomique."""
    try:
        await db.execute(
            text("LOCK TABLE geodata_versions IN SHARE ROW EXCLUSIVE MODE")
        )
    except Exception:
        pass
    target = await db.get(GeodataVersion, target_id)
    if target is None:
        raise HTTPException(status_code=404, detail="Version inconnue")
    if target.is_active:
        await db.refresh(target)
        return target
    await db.execute(
        update(GeodataVersion)
        .where(GeodataVersion.is_active.is_(True))
        .values(is_active=False)
    )
    target.is_active = True
    await db.flush()
    await db.refresh(target)
    return target


async def delete_version(db: AsyncSession, version_id: uuid.UUID) -> None:
    version = await db.get(GeodataVersion, version_id)
    if version is None:
        raise HTTPException(status_code=404, detail="Version inconnue")
    if version.is_active:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Impossible de supprimer la version active",
        )
    await db.delete(version)
    await db.flush()


async def get_known_region_names_normalized(db: AsyncSession) -> set[str]:
    from app.models.geography import Region

    rows = (await db.execute(select(Region.name))).scalars().all()
    return {_norm(r) for r in rows}
