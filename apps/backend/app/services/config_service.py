from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.site_config import SiteConfiguration


async def get_config(db: AsyncSession, key: str) -> SiteConfiguration | None:
    result = await db.execute(
        select(SiteConfiguration).where(SiteConfiguration.key == key)
    )
    return result.scalar_one_or_none()


async def update_config(
    db: AsyncSession, key: str, value: str
) -> SiteConfiguration:
    config = await get_config(db, key)
    if not config:
        config = SiteConfiguration(key=key, value=value)
        config.updated_at = datetime.now(UTC)
        db.add(config)
    else:
        config.value = value
        config.updated_at = datetime.now(UTC)

    await db.commit()
    await db.refresh(config)
    return config


async def get_public_globalleaks_url(db: AsyncSession) -> str:
    config = await get_config(db, "globalleaks_url")
    return config.value if config else ""
