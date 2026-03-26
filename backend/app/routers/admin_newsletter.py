from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_role
from app.schemas.newsletter import PaginatedSubscribers
from app.services import newsletter_service

router = APIRouter(
    prefix="/api/admin/newsletter",
    tags=["admin-newsletter"],
    dependencies=[Depends(require_role("admin"))],
)


@router.get("/subscribers", response_model=PaginatedSubscribers)
async def list_subscribers(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    status: str | None = Query(None),
    search: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    return await newsletter_service.list_subscribers(
        db, page=page, per_page=per_page, status=status, search=search
    )


@router.get("/export")
async def export_subscribers(db: AsyncSession = Depends(get_db)):
    csv_content = await newsletter_service.export_csv(db)
    from datetime import date

    filename = f"abonnes_newsletter_{date.today().isoformat()}.csv"
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.delete("/subscribers/{subscriber_id}", status_code=204)
async def delete_subscriber(
    subscriber_id: str,
    db: AsyncSession = Depends(get_db),
):
    deleted = await newsletter_service.delete_subscriber(db, subscriber_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Abonne non trouve")
