from datetime import UTC, datetime, timedelta

from sqlalchemy import Date, cast, delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.visit_log import VisitLog
from app.schemas.analytics import (
    DashboardResponse,
    DataRetentionInfo,
    DownloadStats,
    PurgeResponse,
    TrendItem,
    VisitStats,
)


def _get_period_start(period: str) -> datetime:
    now = datetime.now(UTC)
    if period == "7d":
        return now - timedelta(days=7)
    elif period == "12m":
        return now - timedelta(days=365)
    else:  # 30d default
        return now - timedelta(days=30)


async def get_dashboard(
    db: AsyncSession, period: str = "30d"
) -> DashboardResponse:
    period_start = _get_period_start(period)

    base_filter = VisitLog.created_at >= period_start

    # Visit stats
    visit_total = (
        await db.execute(
            select(func.count())
            .select_from(VisitLog)
            .where(base_filter, VisitLog.event_type == "page_view")
        )
    ).scalar() or 0

    visit_by_type_result = await db.execute(
        select(VisitLog.page_type, func.count())
        .where(base_filter, VisitLog.event_type == "page_view")
        .group_by(VisitLog.page_type)
    )
    visit_by_type = {
        row[0] or "other": row[1] for row in visit_by_type_result
    }

    visit_trend_result = await db.execute(
        select(
            cast(VisitLog.created_at, Date).label("date"),
            func.count().label("count"),
        )
        .where(base_filter, VisitLog.event_type == "page_view")
        .group_by("date")
        .order_by("date")
    )
    visit_trend = [
        TrendItem(date=str(row.date), count=row.count)
        for row in visit_trend_result
    ]

    # Download stats
    dl_total = (
        await db.execute(
            select(func.count())
            .select_from(VisitLog)
            .where(base_filter, VisitLog.event_type == "download")
        )
    ).scalar() or 0

    dl_by_format_result = await db.execute(
        select(VisitLog.download_format, func.count())
        .where(base_filter, VisitLog.event_type == "download")
        .group_by(VisitLog.download_format)
    )
    dl_by_format = {
        row[0] or "other": row[1] for row in dl_by_format_result
    }

    dl_trend_result = await db.execute(
        select(
            cast(VisitLog.created_at, Date).label("date"),
            func.count().label("count"),
        )
        .where(base_filter, VisitLog.event_type == "download")
        .group_by("date")
        .order_by("date")
    )
    dl_trend = [
        TrendItem(date=str(row.date), count=row.count)
        for row in dl_trend_result
    ]

    # Data retention
    oldest = (
        await db.execute(
            select(func.min(VisitLog.created_at))
        )
    ).scalar()

    twelve_months_ago = datetime.now(UTC) - timedelta(days=365)
    purge_count = (
        await db.execute(
            select(func.count())
            .select_from(VisitLog)
            .where(VisitLog.created_at < twelve_months_ago)
        )
    ).scalar() or 0

    return DashboardResponse(
        period=period,
        visits=VisitStats(
            total=visit_total,
            by_page_type=visit_by_type,
            trend=visit_trend,
        ),
        downloads=DownloadStats(
            total=dl_total,
            by_format=dl_by_format,
            trend=dl_trend,
        ),
        data_retention=DataRetentionInfo(
            oldest_record=oldest,
            purge_eligible_count=purge_count,
            purge_eligible=purge_count > 0,
        ),
    )


async def purge_old_records(db: AsyncSession) -> PurgeResponse:
    twelve_months_ago = datetime.now(UTC) - timedelta(days=365)

    result = await db.execute(
        delete(VisitLog).where(VisitLog.created_at < twelve_months_ago)
    )
    await db.commit()

    count = result.rowcount
    return PurgeResponse(
        purged_count=count,
        message=f"{count} enregistrements de plus de 12 mois ont ete supprimes.",
    )
