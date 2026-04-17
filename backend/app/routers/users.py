import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user, hash_password, require_role
from app.models.user import User, UserRole
from app.schemas.auth import UserResponse

router = APIRouter(
    prefix="/api/admin/users",
    tags=["admin-users"],
    dependencies=[Depends(require_role("admin"))],
)


@router.get("", response_model=list[UserResponse])
async def list_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(User).order_by(User.created_at.desc())
    )
    return list(result.scalars().all())


@router.post("", response_model=UserResponse, status_code=201)
async def create_user(
    email: str,
    password: str,
    role: str = "editor",
    db: AsyncSession = Depends(get_db),
):
    existing = await db.execute(select(User).where(User.email == email.lower()))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email deja utilise")

    if role not in ("admin", "editor"):
        raise HTTPException(status_code=400, detail="Role invalide")

    user = User(
        email=email.lower(),
        hashed_password=hash_password(password),
        role=UserRole(role),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: uuid.UUID,
    role: str | None = None,
    is_active: bool | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouve")

    if role is not None:
        if role not in ("admin", "editor"):
            raise HTTPException(status_code=400, detail="Role invalide")
        user.role = UserRole(role)

    if is_active is not None:
        if user.id == current_user.id and not is_active:
            raise HTTPException(
                status_code=400,
                detail="Impossible de desactiver votre propre compte",
            )
        user.is_active = is_active

    await db.commit()
    await db.refresh(user)
    return user


@router.delete("/{user_id}", response_model=UserResponse)
async def deactivate_user(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouve")

    if user.id == current_user.id:
        raise HTTPException(
            status_code=400,
            detail="Impossible de desactiver votre propre compte",
        )

    user.is_active = False
    await db.commit()
    await db.refresh(user)
    return user
