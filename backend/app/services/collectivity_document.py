import uuid
from pathlib import Path

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.collectivity_document import CollectivityDocument
from app.models.geography import Commune, Province, Region

_PARENT_MODEL = {
    "province": Province,
    "region": Region,
    "commune": Commune,
}

_PARENT_FK_COLUMN = {
    "province": CollectivityDocument.province_id,
    "region": CollectivityDocument.region_id,
    "commune": CollectivityDocument.commune_id,
}


def _parent_filter(parent_type: str, parent_id: uuid.UUID):
    column = _PARENT_FK_COLUMN[parent_type]
    return column == parent_id


async def parent_exists(
    db: AsyncSession, parent_type: str, parent_id: uuid.UUID
) -> bool:
    model = _PARENT_MODEL.get(parent_type)
    if model is None:
        return False
    result = await db.execute(select(model.id).where(model.id == parent_id))
    return result.scalar_one_or_none() is not None


async def list_for_parent(
    db: AsyncSession, parent_type: str, parent_id: uuid.UUID
) -> list[CollectivityDocument]:
    result = await db.execute(
        select(CollectivityDocument)
        .where(_parent_filter(parent_type, parent_id))
        .order_by(CollectivityDocument.position, CollectivityDocument.created_at)
    )
    return list(result.scalars().all())


async def next_position(
    db: AsyncSession, parent_type: str, parent_id: uuid.UUID
) -> int:
    result = await db.execute(
        select(func.coalesce(func.max(CollectivityDocument.position), -1)).where(
            _parent_filter(parent_type, parent_id)
        )
    )
    max_pos = result.scalar_one()
    return int(max_pos) + 1


async def create(
    db: AsyncSession,
    parent_type: str,
    parent_id: uuid.UUID,
    title: str,
    file_path: str,
    file_mime: str,
    file_size_bytes: int,
) -> CollectivityDocument:
    position = await next_position(db, parent_type, parent_id)
    kwargs = {
        "title": title,
        "file_path": file_path,
        "file_mime": file_mime,
        "file_size_bytes": file_size_bytes,
        "position": position,
        f"{parent_type}_id": parent_id,
    }
    doc = CollectivityDocument(**kwargs)
    db.add(doc)
    await db.commit()
    await db.refresh(doc)
    return doc


async def get_by_id(
    db: AsyncSession, doc_id: uuid.UUID
) -> CollectivityDocument | None:
    result = await db.execute(
        select(CollectivityDocument).where(CollectivityDocument.id == doc_id)
    )
    return result.scalar_one_or_none()


async def update_title(
    db: AsyncSession, doc: CollectivityDocument, title: str
) -> CollectivityDocument:
    doc.title = title
    await db.commit()
    await db.refresh(doc)
    return doc


async def replace_file(
    db: AsyncSession,
    doc: CollectivityDocument,
    file_path: str,
    file_mime: str,
    file_size_bytes: int,
) -> CollectivityDocument:
    old_path = doc.file_path
    doc.file_path = file_path
    doc.file_mime = file_mime
    doc.file_size_bytes = file_size_bytes
    await db.commit()
    await db.refresh(doc)
    _remove_file_safely(old_path)
    return doc


async def delete(db: AsyncSession, doc: CollectivityDocument) -> None:
    old_path = doc.file_path
    await db.delete(doc)
    await db.commit()
    _remove_file_safely(old_path)


async def reorder(
    db: AsyncSession,
    parent_type: str,
    parent_id: uuid.UUID,
    ordered_ids: list[uuid.UUID],
) -> list[CollectivityDocument] | str:
    existing = await list_for_parent(db, parent_type, parent_id)
    existing_ids = {d.id for d in existing}

    if len(ordered_ids) != len(existing_ids):
        return "ordered_ids doit lister tous les documents du parent"
    if set(ordered_ids) != existing_ids:
        return "ordered_ids contient des documents inconnus pour ce parent"
    if len(set(ordered_ids)) != len(ordered_ids):
        return "ordered_ids contient des doublons"

    by_id = {d.id: d for d in existing}
    for index, doc_id in enumerate(ordered_ids):
        by_id[doc_id].position = index
    await db.commit()
    return await list_for_parent(db, parent_type, parent_id)


def _remove_file_safely(relative_path: str) -> None:
    if not relative_path:
        return
    trimmed = relative_path.lstrip("/")
    path = Path(trimmed)
    try:
        if path.is_file():
            path.unlink()
    except OSError:
        return


def to_read_dict(doc: CollectivityDocument) -> dict:
    return {
        "id": doc.id,
        "parent_type": doc.parent_type,
        "parent_id": doc.parent_id,
        "title": doc.title,
        "file_path": doc.file_path,
        "file_mime": doc.file_mime,
        "file_size_bytes": doc.file_size_bytes,
        "position": doc.position,
        "download_url": doc.file_path,
        "created_at": doc.created_at,
        "updated_at": doc.updated_at,
    }
