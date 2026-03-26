from fastapi import APIRouter, BackgroundTasks, Depends, Query, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import get_db
from app.core.rate_limit import limiter
from app.schemas.newsletter import SubscribeRequest, SubscribeResponse
from app.services import newsletter_service

settings = get_settings()

router = APIRouter(prefix="/api/newsletter", tags=["newsletter"])


@router.post("/subscribe", response_model=SubscribeResponse)
@limiter.limit("5/minute")
async def subscribe(
    request: Request,
    body: SubscribeRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    message = await newsletter_service.subscribe(db, body.email, background_tasks)
    return SubscribeResponse(message=message)


@router.get("/confirm")
async def confirm(
    token: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    success = await newsletter_service.confirm(db, token)
    if success:
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/newsletter/confirmed",
            status_code=302,
        )
    return RedirectResponse(
        url=f"{settings.FRONTEND_URL}/newsletter/confirmed?error=invalid",
        status_code=302,
    )


@router.get("/unsubscribe")
async def unsubscribe_handler(
    token: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    success = await newsletter_service.unsubscribe(db, token)
    if success:
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/newsletter/unsubscribed",
            status_code=302,
        )
    return RedirectResponse(
        url=f"{settings.FRONTEND_URL}/newsletter/unsubscribed?error=invalid",
        status_code=302,
    )
