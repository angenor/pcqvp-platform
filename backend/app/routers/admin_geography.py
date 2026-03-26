import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_role
from app.models.user import User
from app.schemas.geography import (
    CommuneCreate,
    CommuneDetail,
    CommuneList,
    CommuneUpdate,
    PaginatedResponse,
    ProvinceCreate,
    ProvinceDetail,
    ProvinceList,
    ProvinceUpdate,
    RegionCreate,
    RegionDetail,
    RegionList,
    RegionUpdate,
)
from app.services.geography import (
    create_commune,
    create_province,
    create_region,
    delete_commune,
    delete_province,
    delete_region,
    get_commune_by_id,
    get_province_by_id,
    get_region_by_id,
    list_communes,
    list_provinces,
    list_regions,
    update_commune,
    update_province,
    update_region,
)

router = APIRouter(prefix="/api/admin", tags=["admin-geography"])


# --- Provinces ---


@router.get("/provinces", response_model=PaginatedResponse[ProvinceList])
async def admin_list_provinces(
    search: str | None = None,
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(require_role("admin", "editor")),
    db: AsyncSession = Depends(get_db),
):
    items, total = await list_provinces(db, search=search, skip=skip, limit=limit)
    return PaginatedResponse(items=items, total=total)


@router.post("/provinces", response_model=ProvinceDetail, status_code=201)
async def admin_create_province(
    data: ProvinceCreate,
    current_user: User = Depends(require_role("admin", "editor")),
    db: AsyncSession = Depends(get_db),
):
    try:
        desc = data.description_json.model_dump() if data.description_json else None
        return await create_province(db, data.name, data.code, desc)
    except Exception as exc:
        if "unique" in str(exc).lower():
            raise HTTPException(
                status_code=409,
                detail=f"A province with code '{data.code}' already exists",
            )
        raise


@router.put("/provinces/{province_id}", response_model=ProvinceDetail)
async def admin_update_province(
    province_id: uuid.UUID,
    data: ProvinceUpdate,
    current_user: User = Depends(require_role("admin", "editor")),
    db: AsyncSession = Depends(get_db),
):
    province = await get_province_by_id(db, province_id)
    if not province:
        raise HTTPException(status_code=404, detail="Province not found")
    try:
        desc = data.description_json.model_dump() if data.description_json else None
        return await update_province(
            db,
            province,
            data.name,
            data.code,
            desc,
        )
    except Exception as exc:
        if "unique" in str(exc).lower():
            raise HTTPException(
                status_code=409,
                detail=f"A province with code '{data.code}' already exists",
            )
        raise


@router.delete("/provinces/{province_id}", status_code=204)
async def admin_delete_province(
    province_id: uuid.UUID,
    current_user: User = Depends(require_role("admin", "editor")),
    db: AsyncSession = Depends(get_db),
):
    province = await get_province_by_id(db, province_id)
    if not province:
        raise HTTPException(status_code=404, detail="Province not found")
    error = await delete_province(db, province)
    if error:
        raise HTTPException(status_code=409, detail=error)


# --- Regions ---


@router.get("/regions", response_model=PaginatedResponse[RegionList])
async def admin_list_regions(
    province_id: uuid.UUID | None = None,
    search: str | None = None,
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(require_role("admin", "editor")),
    db: AsyncSession = Depends(get_db),
):
    items, total = await list_regions(
        db, province_id=province_id, search=search, skip=skip, limit=limit
    )
    return PaginatedResponse(items=items, total=total)


@router.post("/regions", response_model=RegionDetail, status_code=201)
async def admin_create_region(
    data: RegionCreate,
    current_user: User = Depends(require_role("admin", "editor")),
    db: AsyncSession = Depends(get_db),
):
    try:
        desc = data.description_json.model_dump() if data.description_json else None
        return await create_region(
            db,
            data.name,
            data.code,
            data.province_id,
            desc,
        )
    except Exception as exc:
        if "unique" in str(exc).lower():
            raise HTTPException(
                status_code=409,
                detail=f"A region with code '{data.code}' already exists",
            )
        raise


@router.put("/regions/{region_id}", response_model=RegionDetail)
async def admin_update_region(
    region_id: uuid.UUID,
    data: RegionUpdate,
    current_user: User = Depends(require_role("admin", "editor")),
    db: AsyncSession = Depends(get_db),
):
    region = await get_region_by_id(db, region_id)
    if not region:
        raise HTTPException(status_code=404, detail="Region not found")
    try:
        desc = data.description_json.model_dump() if data.description_json else None
        return await update_region(
            db,
            region,
            data.name,
            data.code,
            data.province_id,
            desc,
        )
    except Exception as exc:
        if "unique" in str(exc).lower():
            raise HTTPException(
                status_code=409,
                detail=f"A region with code '{data.code}' already exists",
            )
        raise


@router.delete("/regions/{region_id}", status_code=204)
async def admin_delete_region(
    region_id: uuid.UUID,
    current_user: User = Depends(require_role("admin", "editor")),
    db: AsyncSession = Depends(get_db),
):
    region = await get_region_by_id(db, region_id)
    if not region:
        raise HTTPException(status_code=404, detail="Region not found")
    error = await delete_region(db, region)
    if error:
        raise HTTPException(status_code=409, detail=error)


# --- Communes ---


@router.get("/communes", response_model=PaginatedResponse[CommuneList])
async def admin_list_communes(
    region_id: uuid.UUID | None = None,
    search: str | None = None,
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(require_role("admin", "editor")),
    db: AsyncSession = Depends(get_db),
):
    items, total = await list_communes(
        db, region_id=region_id, search=search, skip=skip, limit=limit
    )
    return PaginatedResponse(items=items, total=total)


@router.post("/communes", response_model=CommuneDetail, status_code=201)
async def admin_create_commune(
    data: CommuneCreate,
    current_user: User = Depends(require_role("admin", "editor")),
    db: AsyncSession = Depends(get_db),
):
    try:
        desc = data.description_json.model_dump() if data.description_json else None
        return await create_commune(
            db,
            data.name,
            data.code,
            data.region_id,
            desc,
        )
    except Exception as exc:
        if "unique" in str(exc).lower():
            raise HTTPException(
                status_code=409,
                detail=f"A commune with code '{data.code}' already exists",
            )
        raise


@router.put("/communes/{commune_id}", response_model=CommuneDetail)
async def admin_update_commune(
    commune_id: uuid.UUID,
    data: CommuneUpdate,
    current_user: User = Depends(require_role("admin", "editor")),
    db: AsyncSession = Depends(get_db),
):
    commune = await get_commune_by_id(db, commune_id)
    if not commune:
        raise HTTPException(status_code=404, detail="Commune not found")
    try:
        desc = data.description_json.model_dump() if data.description_json else None
        return await update_commune(
            db,
            commune,
            data.name,
            data.code,
            data.region_id,
            desc,
        )
    except Exception as exc:
        if "unique" in str(exc).lower():
            raise HTTPException(
                status_code=409,
                detail=f"A commune with code '{data.code}' already exists",
            )
        raise


@router.delete("/communes/{commune_id}", status_code=204)
async def admin_delete_commune(
    commune_id: uuid.UUID,
    current_user: User = Depends(require_role("admin", "editor")),
    db: AsyncSession = Depends(get_db),
):
    commune = await get_commune_by_id(db, commune_id)
    if not commune:
        raise HTTPException(status_code=404, detail="Commune not found")
    await delete_commune(db, commune)
