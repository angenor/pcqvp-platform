from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_role
from app.schemas.analytics import DashboardResponse, PurgeResponse
from app.services import analytics_service

router = APIRouter(
    prefix="/api/admin/analytics",
    tags=["admin-analytics"],
    dependencies=[Depends(require_role("admin"))],
)


@router.get("/dashboard", response_model=DashboardResponse)
async def dashboard(
    period: str = Query("30d", pattern="^(7d|30d|12m)$"),
    db: AsyncSession = Depends(get_db),
):
    return await analytics_service.get_dashboard(db, period)


@router.delete("/purge", response_model=PurgeResponse)
async def purge(db: AsyncSession = Depends(get_db)):
    return await analytics_service.purge_old_records(db)
