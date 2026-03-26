from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_role
from app.models.compte_administratif import CompteAdministratif, CompteStatus
from app.models.geography import Commune, Province, Region
from app.models.user import User
from app.models.visit_log import VisitLog
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


@router.get("/stats")
async def stats(db: AsyncSession = Depends(get_db)):
    # Comptes administratifs
    total_comptes = (
        await db.execute(select(func.count()).select_from(CompteAdministratif))
    ).scalar() or 0
    published_comptes = (
        await db.execute(
            select(func.count())
            .select_from(CompteAdministratif)
            .where(CompteAdministratif.status == CompteStatus.published)
        )
    ).scalar() or 0
    draft_comptes = total_comptes - published_comptes

    # Collectivites
    provinces_count = (
        await db.execute(select(func.count()).select_from(Province))
    ).scalar() or 0
    regions_count = (
        await db.execute(select(func.count()).select_from(Region))
    ).scalar() or 0
    communes_count = (
        await db.execute(select(func.count()).select_from(Commune))
    ).scalar() or 0

    # Users
    users_count = (
        await db.execute(select(func.count()).select_from(User))
    ).scalar() or 0

    # Downloads
    downloads_count = (
        await db.execute(
            select(func.count())
            .select_from(VisitLog)
            .where(VisitLog.event_type == "download")
        )
    ).scalar() or 0

    return {
        "comptes": {
            "total": total_comptes,
            "published": published_comptes,
            "draft": draft_comptes,
        },
        "collectivites": {
            "provinces": provinces_count,
            "regions": regions_count,
            "communes": communes_count,
        },
        "users": users_count,
        "downloads": downloads_count,
    }


@router.delete("/purge", response_model=PurgeResponse)
async def purge(db: AsyncSession = Depends(get_db)):
    return await analytics_service.purge_old_records(db)
