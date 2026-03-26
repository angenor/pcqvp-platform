from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.site_config import GlobalLeaksPublicResponse
from app.services import config_service

router = APIRouter(prefix="/api/public/config", tags=["public-config"])


@router.get("/globalleaks", response_model=GlobalLeaksPublicResponse)
async def get_globalleaks_url(db: AsyncSession = Depends(get_db)):
    url = await config_service.get_public_globalleaks_url(db)
    return GlobalLeaksPublicResponse(url=url)
