import asyncio

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from sqlalchemy import text

from app.core.config import get_settings
from app.core.database import engine
from app.core.rate_limit import limiter, rate_limit_exceeded_handler
from app.middleware.visit_tracker import VisitTrackerMiddleware
from app.routers.admin_analytics import router as admin_analytics_router
from app.routers.admin_comptes import router as admin_comptes_router
from app.routers.admin_config import router as admin_config_router
from app.routers.admin_geography import router as admin_geography_router
from app.routers.admin_newsletter import router as admin_newsletter_router
from app.routers.admin_templates import router as admin_templates_router
from app.routers.auth import router as auth_router
from app.routers.geography import router as geography_router
from app.routers.newsletter import router as newsletter_router
from app.routers.public_comptes import router as public_comptes_router
from app.routers.public_config import router as public_config_router
from app.routers.search import router as search_router

settings = get_settings()

app = FastAPI(title="PCQVP Platform")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

app.add_middleware(VisitTrackerMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_router)
app.include_router(geography_router)
app.include_router(public_comptes_router)
app.include_router(admin_geography_router)
app.include_router(admin_templates_router)
app.include_router(admin_comptes_router)
app.include_router(search_router)
app.include_router(newsletter_router)
app.include_router(admin_newsletter_router)
app.include_router(admin_analytics_router)
app.include_router(admin_config_router)
app.include_router(public_config_router)


@app.get("/health")
async def health():
    try:
        async with asyncio.timeout(2.0):
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
        return {"status": "ok", "db": "connected"}
    except Exception as exc:
        return JSONResponse(
            status_code=503,
            content={"status": "ok", "db": "disconnected", "detail": str(exc)},
        )
