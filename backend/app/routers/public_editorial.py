from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.editorial import (
    BodyContentPublic,
    ContactInfoPublic,
    EditorialPublicResponse,
    FooterAboutContentPublic,
    FooterContentPublic,
    HeroContentPublic,
    ResourceLinkPublic,
)
from app.services.editorial import (
    get_body,
    get_contact,
    get_footer_about,
    get_hero,
    list_resources,
)

router = APIRouter(prefix="/api/editorial", tags=["public-editorial"])


@router.get("", response_model=EditorialPublicResponse)
async def get_editorial(db: AsyncSession = Depends(get_db)):
    hero_data = await get_hero(db)
    body = await get_body(db)
    footer_about = await get_footer_about(db)
    contact = await get_contact(db)
    resources = await list_resources(db)

    def hero_text(row, default: str = "") -> str:
        return row.content_text if row and row.content_text else default

    return EditorialPublicResponse(
        hero=HeroContentPublic(
            title=hero_text(hero_data["title"]),
            subtitle=hero_text(hero_data["subtitle"]),
            description=hero_text(hero_data["description"]),
        ),
        body=BodyContentPublic(
            content_json=body.content_json if body else None,
        ),
        footer=FooterContentPublic(
            about=FooterAboutContentPublic(
                content_json=footer_about.content_json
                if footer_about
                else None,
            ),
            contact=ContactInfoPublic(
                email=contact.email if contact else None,
                phone=contact.phone if contact else None,
                address=contact.address if contact else None,
            ),
            resources=[
                ResourceLinkPublic.model_validate(r) for r in resources
            ],
        ),
    )
