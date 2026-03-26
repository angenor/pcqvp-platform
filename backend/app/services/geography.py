import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.geography import Commune, Province, Region

# --- Province ---


async def create_province(
    db: AsyncSession, name: str, code: str, description_json: dict | None = None
) -> Province:
    province = Province(name=name, code=code, description_json=description_json)
    db.add(province)
    await db.commit()
    await db.refresh(province)
    return province


async def get_province_by_id(
    db: AsyncSession, province_id: uuid.UUID
) -> Province | None:
    result = await db.execute(
        select(Province)
        .options(selectinload(Province.regions))
        .where(Province.id == province_id)
    )
    return result.scalar_one_or_none()


async def list_provinces(
    db: AsyncSession,
    search: str | None = None,
    skip: int = 0,
    limit: int | None = None,
) -> tuple[list[Province], int]:
    query = select(Province).order_by(Province.name)
    count_query = select(func.count()).select_from(Province)

    if search:
        query = query.where(Province.name.ilike(f"%{search}%"))
        count_query = count_query.where(Province.name.ilike(f"%{search}%"))

    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    if skip:
        query = query.offset(skip)
    if limit is not None:
        query = query.limit(limit)

    result = await db.execute(query)
    return list(result.scalars().all()), total


async def update_province(
    db: AsyncSession,
    province: Province,
    name: str,
    code: str,
    description_json: dict | None = None,
) -> Province:
    province.name = name
    province.code = code
    if description_json is not None:
        province.description_json = description_json
    await db.commit()
    await db.refresh(province)
    return province


async def delete_province(db: AsyncSession, province: Province) -> str | None:
    count_result = await db.execute(
        select(func.count())
        .select_from(Region)
        .where(Region.province_id == province.id)
    )
    child_count = count_result.scalar_one()
    if child_count > 0:
        return f"Cannot delete province: it has {child_count} region(s)"
    await db.delete(province)
    await db.commit()
    return None


# --- Region ---


async def create_region(
    db: AsyncSession,
    name: str,
    code: str,
    province_id: uuid.UUID,
    description_json: dict | None = None,
) -> Region:
    region = Region(
        name=name,
        code=code,
        province_id=province_id,
        description_json=description_json,
    )
    db.add(region)
    await db.commit()
    await db.refresh(region)
    return region


async def get_region_by_id(db: AsyncSession, region_id: uuid.UUID) -> Region | None:
    result = await db.execute(
        select(Region)
        .options(selectinload(Region.communes))
        .where(Region.id == region_id)
    )
    return result.scalar_one_or_none()


async def list_regions(
    db: AsyncSession,
    province_id: uuid.UUID | None = None,
    search: str | None = None,
    skip: int = 0,
    limit: int | None = None,
) -> tuple[list[Region], int]:
    query = select(Region).order_by(Region.name)
    count_query = select(func.count()).select_from(Region)

    if province_id:
        query = query.where(Region.province_id == province_id)
        count_query = count_query.where(Region.province_id == province_id)
    if search:
        query = query.where(Region.name.ilike(f"%{search}%"))
        count_query = count_query.where(Region.name.ilike(f"%{search}%"))

    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    if skip:
        query = query.offset(skip)
    if limit is not None:
        query = query.limit(limit)

    result = await db.execute(query)
    return list(result.scalars().all()), total


async def update_region(
    db: AsyncSession,
    region: Region,
    name: str,
    code: str,
    province_id: uuid.UUID,
    description_json: dict | None = None,
) -> Region:
    region.name = name
    region.code = code
    region.province_id = province_id
    if description_json is not None:
        region.description_json = description_json
    await db.commit()
    await db.refresh(region)
    return region


async def delete_region(db: AsyncSession, region: Region) -> str | None:
    count_result = await db.execute(
        select(func.count()).select_from(Commune).where(Commune.region_id == region.id)
    )
    child_count = count_result.scalar_one()
    if child_count > 0:
        return f"Cannot delete region: it has {child_count} commune(s)"
    await db.delete(region)
    await db.commit()
    return None


# --- Commune ---


async def create_commune(
    db: AsyncSession,
    name: str,
    code: str,
    region_id: uuid.UUID,
    description_json: dict | None = None,
) -> Commune:
    commune = Commune(
        name=name,
        code=code,
        region_id=region_id,
        description_json=description_json,
    )
    db.add(commune)
    await db.commit()
    await db.refresh(commune)
    return commune


async def get_commune_by_id(db: AsyncSession, commune_id: uuid.UUID) -> Commune | None:
    result = await db.execute(select(Commune).where(Commune.id == commune_id))
    return result.scalar_one_or_none()


async def list_communes(
    db: AsyncSession,
    region_id: uuid.UUID | None = None,
    search: str | None = None,
    skip: int = 0,
    limit: int | None = None,
) -> tuple[list[Commune], int]:
    query = select(Commune).order_by(Commune.name)
    count_query = select(func.count()).select_from(Commune)

    if region_id:
        query = query.where(Commune.region_id == region_id)
        count_query = count_query.where(Commune.region_id == region_id)
    if search:
        query = query.where(Commune.name.ilike(f"%{search}%"))
        count_query = count_query.where(Commune.name.ilike(f"%{search}%"))

    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    if skip:
        query = query.offset(skip)
    if limit is not None:
        query = query.limit(limit)

    result = await db.execute(query)
    return list(result.scalars().all()), total


async def update_commune(
    db: AsyncSession,
    commune: Commune,
    name: str,
    code: str,
    region_id: uuid.UUID,
    description_json: dict | None = None,
) -> Commune:
    commune.name = name
    commune.code = code
    commune.region_id = region_id
    if description_json is not None:
        commune.description_json = description_json
    await db.commit()
    await db.refresh(commune)
    return commune


async def delete_commune(db: AsyncSession, commune: Commune) -> None:
    await db.delete(commune)
    await db.commit()


# --- Hierarchy ---


async def get_hierarchy(db: AsyncSession) -> list[Province]:
    result = await db.execute(
        select(Province)
        .options(selectinload(Province.regions).selectinload(Region.communes))
        .order_by(Province.name)
    )
    return list(result.scalars().unique().all())
