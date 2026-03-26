from fastapi import APIRouter, Cookie, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decode_token, get_current_user, require_role
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserResponse
from app.services.auth import authenticate_user, refresh_access_token, register_user

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(
    data: LoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    result = await authenticate_user(db, data.email, data.password, response)

    if result == "locked":
        raise HTTPException(status_code=423, detail="Compte temporairement verrouille")

    if result is None:
        raise HTTPException(status_code=401, detail="Identifiants incorrects")

    return result


@router.get("/me", response_model=UserResponse)
async def me(
    current_user: User = Depends(get_current_user),
):
    return current_user


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(
    data: RegisterRequest,
    current_user: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    user = await register_user(db, data.email, data.password, data.role)
    if user is None:
        raise HTTPException(
            status_code=400, detail="Un compte avec cet email existe deja"
        )
    return user


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    response: Response,
    refresh_token: str | None = Cookie(default=None),
    db: AsyncSession = Depends(get_db),
):
    if not refresh_token:
        raise HTTPException(
            status_code=401, detail="Token de rafraichissement invalide ou expire"
        )

    payload = decode_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=401, detail="Token de rafraichissement invalide ou expire"
        )

    result = await refresh_access_token(db, payload["sub"], response)
    if result is None:
        raise HTTPException(
            status_code=401, detail="Token de rafraichissement invalide ou expire"
        )

    return result
