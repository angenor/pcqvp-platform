from datetime import UTC, datetime, timedelta

from fastapi import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)
from app.models.user import User, UserRole
from app.schemas.auth import TokenResponse

settings = get_settings()

LOCKOUT_THRESHOLD = 5
LOCKOUT_DURATION_MINUTES = 15


async def authenticate_user(
    db: AsyncSession, email: str, password: str, response: Response
) -> TokenResponse:
    result = await db.execute(select(User).where(User.email == email.lower()))
    user = result.scalar_one_or_none()

    if not user:
        return None

    if not user.is_active:
        return None

    now = datetime.now(UTC)
    if user.locked_until and user.locked_until > now:
        return "locked"

    if not verify_password(password, user.hashed_password):
        user.failed_login_attempts += 1
        if user.failed_login_attempts >= LOCKOUT_THRESHOLD:
            user.locked_until = now + timedelta(minutes=LOCKOUT_DURATION_MINUTES)
        await db.commit()
        return None

    user.failed_login_attempts = 0
    user.locked_until = None
    await db.commit()

    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id))

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        path="/api/auth",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
    )

    return TokenResponse(access_token=access_token)


async def register_user(
    db: AsyncSession, email: str, password: str, role: str = "editor"
) -> User | None:
    result = await db.execute(select(User).where(User.email == email.lower()))
    if result.scalar_one_or_none():
        return None

    user = User(
        email=email.lower(),
        hashed_password=hash_password(password),
        role=UserRole(role),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def refresh_access_token(
    db: AsyncSession, user_id: str, response: Response
) -> TokenResponse | None:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        return None

    access_token = create_access_token(str(user.id))
    new_refresh_token = create_refresh_token(str(user.id))

    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        path="/api/auth",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
    )

    return TokenResponse(access_token=access_token)
