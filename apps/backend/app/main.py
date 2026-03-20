import asyncio

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.core.config import get_settings
from app.core.database import engine
from app.routers.auth import router as auth_router

settings = get_settings()

app = FastAPI(title="PCQVP Platform")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_router)


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
