import uuid

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.compte_administratif import CompteAdministratif, CompteStatus
from app.models.geography import Commune, Province, Region

# --- Province ---


async def create_province(
    db: AsyncSession,
    name: str,
    code: str,
    description_json: dict | None = None,
    banner_image: str | None = None,
) -> Province:
    province = Province(
        name=name, code=code, description_json=description_json, banner_image=banner_image
    )
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
    has_comptes: bool = False,
) -> tuple[list[Province], int]:
    query = select(Province).order_by(Province.name)
    count_query = select(func.count()).select_from(Province)

    if has_comptes:
        # Provinces ayant au moins une commune avec un compte publié
        province_ids_via_communes = (
            select(Province.id)
            .join(Region, Region.province_id == Province.id)
            .join(Commune, Commune.region_id == Region.id)
            .join(
                CompteAdministratif,
                and_(
                    CompteAdministratif.collectivite_type == "commune",
                    CompteAdministratif.collectivite_id == Commune.id,
                    CompteAdministratif.status == CompteStatus.published,
                ),
            )
            .distinct()
        )
        # Provinces ayant au moins une région avec un compte publié (type région)
        province_ids_via_regions = (
            select(Province.id)
            .join(Region, Region.province_id == Province.id)
            .join(
                CompteAdministratif,
                and_(
                    CompteAdministratif.collectivite_type == "region",
                    CompteAdministratif.collectivite_id == Region.id,
                    CompteAdministratif.status == CompteStatus.published,
                ),
            )
            .distinct()
        )
        has_comptes_filter = Province.id.in_(province_ids_via_communes) | Province.id.in_(
            province_ids_via_regions
        )
        query = query.where(has_comptes_filter)
        count_query = count_query.where(has_comptes_filter)

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
    banner_image: str | None = None,
) -> Province:
    province.name = name
    province.code = code
    if description_json is not None:
        province.description_json = description_json
    province.banner_image = banner_image
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
    banner_image: str | None = None,
) -> Region:
    region = Region(
        name=name,
        code=code,
        province_id=province_id,
        description_json=description_json,
        banner_image=banner_image,
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
    has_comptes: bool = False,
) -> tuple[list[Region], int]:
    query = select(Region).order_by(Region.name)
    count_query = select(func.count()).select_from(Region)

    if has_comptes:
        # Régions ayant au moins une commune avec un compte publié
        region_ids_via_communes = (
            select(Region.id)
            .join(Commune, Commune.region_id == Region.id)
            .join(
                CompteAdministratif,
                and_(
                    CompteAdministratif.collectivite_type == "commune",
                    CompteAdministratif.collectivite_id == Commune.id,
                    CompteAdministratif.status == CompteStatus.published,
                ),
            )
            .distinct()
        )
        # Régions ayant un compte direct publié
        region_ids_direct = (
            select(CompteAdministratif.collectivite_id)
            .where(
                CompteAdministratif.collectivite_type == "region",
                CompteAdministratif.status == CompteStatus.published,
            )
            .distinct()
        )
        has_comptes_filter = Region.id.in_(region_ids_via_communes) | Region.id.in_(
            region_ids_direct
        )
        query = query.where(has_comptes_filter)
        count_query = count_query.where(has_comptes_filter)

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
    banner_image: str | None = None,
) -> Region:
    region.name = name
    region.code = code
    region.province_id = province_id
    if description_json is not None:
        region.description_json = description_json
    region.banner_image = banner_image
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
    banner_image: str | None = None,
) -> Commune:
    commune = Commune(
        name=name,
        code=code,
        region_id=region_id,
        description_json=description_json,
        banner_image=banner_image,
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
    has_comptes: bool = False,
) -> tuple[list[Commune], int]:
    query = select(Commune).order_by(Commune.name)
    count_query = select(func.count()).select_from(Commune)

    if has_comptes:
        commune_ids_with_comptes = (
            select(CompteAdministratif.collectivite_id)
            .where(
                CompteAdministratif.collectivite_type == "commune",
                CompteAdministratif.status == CompteStatus.published,
            )
            .distinct()
        )
        query = query.where(Commune.id.in_(commune_ids_with_comptes))
        count_query = count_query.where(Commune.id.in_(commune_ids_with_comptes))

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
    banner_image: str | None = None,
) -> Commune:
    commune.name = name
    commune.code = code
    commune.region_id = region_id
    if description_json is not None:
        commune.description_json = description_json
    commune.banner_image = banner_image
    await db.commit()
    await db.refresh(commune)
    return commune


async def delete_commune(db: AsyncSession, commune: Commune) -> None:
    await db.delete(commune)
    await db.commit()


# --- IDs with comptes ---


async def get_ids_with_comptes(
    db: AsyncSession,
) -> dict[str, list[uuid.UUID]]:
    """Return IDs of provinces, regions and communes that have comptes administratifs
    (directly or via their children)."""

    # Commune IDs with direct comptes
    commune_result = await db.execute(
        select(CompteAdministratif.collectivite_id)
        .where(CompteAdministratif.collectivite_type == "commune")
        .distinct()
    )
    commune_ids = list(commune_result.scalars().all())

    # Region IDs: direct comptes OR has communes with comptes
    region_direct = (
        select(CompteAdministratif.collectivite_id)
        .where(CompteAdministratif.collectivite_type == "region")
        .distinct()
    )
    region_via_communes = (
        select(Commune.region_id)
        .where(Commune.id.in_(commune_ids))
        .distinct()
    ) if commune_ids else None

    region_result = await db.execute(region_direct)
    region_ids = set(region_result.scalars().all())

    if region_via_communes is not None:
        region_via_result = await db.execute(region_via_communes)
        region_ids.update(region_via_result.scalars().all())

    region_ids_list = list(region_ids)

    # Province IDs: direct comptes OR has regions with comptes
    province_direct = (
        select(CompteAdministratif.collectivite_id)
        .where(CompteAdministratif.collectivite_type == "province")
        .distinct()
    )
    province_via_regions = (
        select(Region.province_id)
        .where(Region.id.in_(region_ids_list))
        .distinct()
    ) if region_ids_list else None

    province_result = await db.execute(province_direct)
    province_ids = set(province_result.scalars().all())

    if province_via_regions is not None:
        province_via_result = await db.execute(province_via_regions)
        province_ids.update(province_via_result.scalars().all())

    return {
        "province_ids": list(province_ids),
        "region_ids": region_ids_list,
        "commune_ids": commune_ids,
    }


# --- Hierarchy ---


async def get_hierarchy(db: AsyncSession) -> list[Province]:
    result = await db.execute(
        select(Province)
        .options(selectinload(Province.regions).selectinload(Region.communes))
        .order_by(Province.name)
    )
    return list(result.scalars().unique().all())
