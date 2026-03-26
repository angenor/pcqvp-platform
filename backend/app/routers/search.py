from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.rate_limit import limiter
from app.schemas.search import SearchResponse
from app.services.search_service import search_fulltext

router = APIRouter(prefix="/api", tags=["search"])


@router.get("/search", response_model=SearchResponse)
@limiter.limit("30/minute")
async def search(
    request: Request,
    q: str = Query(..., min_length=2, max_length=200),
    limit: int = Query(10, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
):
    return await search_fulltext(db, q, limit)
