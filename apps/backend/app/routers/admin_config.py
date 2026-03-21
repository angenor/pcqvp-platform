from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_role
from app.schemas.site_config import ConfigResponse, ConfigUpdateRequest
from app.services import config_service

router = APIRouter(
    prefix="/api/admin/config",
    tags=["admin-config"],
    dependencies=[Depends(require_role("admin"))],
)


@router.get("/{key}", response_model=ConfigResponse)
async def get_config(key: str, db: AsyncSession = Depends(get_db)):
    config = await config_service.get_config(db, key)
    if not config:
        raise HTTPException(status_code=404, detail="Configuration non trouvee")
    return config


@router.put("/{key}", response_model=ConfigResponse)
async def update_config(
    key: str,
    body: ConfigUpdateRequest,
    db: AsyncSession = Depends(get_db),
):
    return await config_service.update_config(db, key, body.value)
