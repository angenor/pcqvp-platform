import uuid

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import get_db
from app.services import geodata_service
from app.schemas.geography import (
    CommuneDetail,
    CommuneList,
    HierarchyProvince,
    ProvinceDetail,
    ProvinceList,
    RegionDetail,
    RegionList,
)
from app.services import collectivity_document as documents_service
from app.services.geography import (
    get_commune_by_id,
    get_hierarchy,
    get_province_by_id,
    get_region_by_id,
    list_communes,
    list_provinces,
    list_regions,
)

router = APIRouter(prefix="/api", tags=["geography"])


async def _attach_documents(
    db: AsyncSession,
    entity,
    parent_type: str,
    schema_class,
):
    documents = await documents_service.list_for_parent(db, parent_type, entity.id)
    payload = schema_class.model_validate(entity).model_dump()
    payload["documents"] = [
        documents_service.to_read_dict(d) for d in documents
    ]
    return schema_class.model_validate(payload)


@router.get("/provinces", response_model=list[ProvinceList])
async def get_provinces(
    has_comptes: bool = False,
    db: AsyncSession = Depends(get_db),
):
    provinces, _ = await list_provinces(db, has_comptes=has_comptes)
    return provinces


@router.get("/provinces/{province_id}", response_model=ProvinceDetail)
async def get_province(province_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    province = await get_province_by_id(db, province_id)
    if not province:
        raise HTTPException(status_code=404, detail="Province not found")
    return await _attach_documents(db, province, "province", ProvinceDetail)


@router.get("/regions", response_model=list[RegionList])
async def get_regions(
    province_id: uuid.UUID | None = None,
    has_comptes: bool = False,
    db: AsyncSession = Depends(get_db),
):
    regions, _ = await list_regions(
        db, province_id=province_id, has_comptes=has_comptes
    )
    return regions


@router.get("/regions/{region_id}", response_model=RegionDetail)
async def get_region(region_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    region = await get_region_by_id(db, region_id)
    if not region:
        raise HTTPException(status_code=404, detail="Region not found")
    return await _attach_documents(db, region, "region", RegionDetail)


@router.get("/communes", response_model=list[CommuneList])
async def get_communes(
    region_id: uuid.UUID | None = None,
    has_comptes: bool = False,
    db: AsyncSession = Depends(get_db),
):
    communes, _ = await list_communes(db, region_id=region_id, has_comptes=has_comptes)
    return communes


@router.get("/communes/{commune_id}", response_model=CommuneDetail)
async def get_commune(commune_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    commune = await get_commune_by_id(db, commune_id)
    if not commune:
        raise HTTPException(status_code=404, detail="Commune not found")
    return await _attach_documents(db, commune, "commune", CommuneDetail)


@router.get("/geography/hierarchy", response_model=list[HierarchyProvince])
async def hierarchy(db: AsyncSession = Depends(get_db)):
    return await get_hierarchy(db)


@router.get("/geography/regions/geojson")
async def regions_geojson(
    request: Request, db: AsyncSession = Depends(get_db)
):
    settings = get_settings()
    version = await geodata_service.get_active_version(db)
    if version is None:
        raise HTTPException(
            status_code=503, detail="No active geodata version"
        )
    etag = f'W/"{version.id}"'
    # `no-cache` force le navigateur à revalider via ETag à chaque requête,
    # garantissant un rollover immédiat après activation/rollback côté admin.
    # Le serveur répond 304 si l'ETag correspond → coût réseau minimal.
    cache_header = (
        f"public, max-age=0, must-revalidate, "
        f"stale-while-revalidate={settings.GEODATA_PUBLIC_CACHE_MAX_AGE}"
    )
    if_none_match = request.headers.get("if-none-match")
    if if_none_match and if_none_match.strip() == etag:
        return Response(
            status_code=304,
            headers={"ETag": etag, "Cache-Control": cache_header},
        )
    return JSONResponse(
        content=version.geojson_processed,
        headers={
            "ETag": etag,
            "Cache-Control": cache_header,
            "Content-Type": "application/geo+json",
        },
    )
