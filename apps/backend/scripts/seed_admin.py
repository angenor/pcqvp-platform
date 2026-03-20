import asyncio

from sqlalchemy import select

from app.core.config import get_settings
from app.core.database import async_session
from app.core.security import hash_password
from app.models.user import User, UserRole


async def seed() -> None:
    settings = get_settings()
    email = settings.FIRST_ADMIN_EMAIL.lower()
    password = settings.FIRST_ADMIN_PASSWORD

    async with async_session() as db:
        result = await db.execute(select(User).where(User.email == email))
        if result.scalar_one_or_none():
            print(f"Admin {email} already exists, skipping.")
            return

        user = User(
            email=email,
            hashed_password=hash_password(password),
            role=UserRole.admin,
        )
        db.add(user)
        await db.commit()
        print(f"Admin {email} created successfully.")


if __name__ == "__main__":
    asyncio.run(seed())
