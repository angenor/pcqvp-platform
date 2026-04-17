import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
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
