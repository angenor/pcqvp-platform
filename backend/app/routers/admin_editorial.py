import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_role
from app.models.user import User
from app.schemas.editorial import (
    BodyContentAdmin,
    BodyUpdate,
    ContactInfoResponse,
    ContactInfoUpdate,
    EditorialAdminResponse,
    FooterAboutContentAdmin,
    FooterAboutUpdate,
    FooterContentAdmin,
    HeroContentAdmin,
    HeroFieldAdmin,
    HeroUpdate,
    ResourceLinkCreate,
    ResourceLinkResponse,
    ResourceLinkUpdate,
    ResourceReorder,
)
from app.services.editorial import (
    create_resource,
    delete_resource,
    get_body,
    get_contact,
    get_footer_about,
    get_hero,
    list_resources,
    reorder_resources,
    update_body,
    update_contact,
    update_footer_about,
    update_hero,
    update_resource,
)

router = APIRouter(prefix="/api/admin/editorial", tags=["admin-editorial"])


async def _build_admin_response(db: AsyncSession) -> EditorialAdminResponse:
    hero_data = await get_hero(db)
    body = await get_body(db)
    footer_about = await get_footer_about(db)
    contact = await get_contact(db)
    resources = await list_resources(db)

    def hero_field(row, default: str = "") -> HeroFieldAdmin:
        if row:
            return HeroFieldAdmin(
                value=row.content_text or default,
                updated_at=row.updated_at,
            )
        return HeroFieldAdmin(value=default)

    return EditorialAdminResponse(
        hero=HeroContentAdmin(
            title=hero_field(hero_data["title"]),
            subtitle=hero_field(hero_data["subtitle"]),
            description=hero_field(hero_data["description"]),
        ),
        body=BodyContentAdmin(
            content_json=body.content_json if body else None,
            updated_at=body.updated_at if body else None,
        ),
        footer=FooterContentAdmin(
            about=FooterAboutContentAdmin(
                content_json=footer_about.content_json if footer_about else None,
                updated_at=footer_about.updated_at if footer_about else None,
            ),
            contact=ContactInfoResponse.model_validate(contact)
            if contact
            else ContactInfoResponse(),
            resources=[
                ResourceLinkResponse.model_validate(r) for r in resources
            ],
        ),
    )


@router.get("", response_model=EditorialAdminResponse)
async def get_editorial(
    current_user: User = Depends(require_role("admin", "editor")),
    db: AsyncSession = Depends(get_db),
):
    return await _build_admin_response(db)


@router.put("/hero")
async def put_hero(
    body: HeroUpdate,
    current_user: User = Depends(require_role("admin", "editor")),
    db: AsyncSession = Depends(get_db),
):
    await update_hero(db, body.title, body.subtitle, body.description, current_user.id)
    return {"message": "Hero section mise à jour"}


@router.put("/body")
async def put_body(
    body: BodyUpdate,
    current_user: User = Depends(require_role("admin", "editor")),
    db: AsyncSession = Depends(get_db),
):
    await update_body(db, body.content_json.model_dump(), current_user.id)
    return {"message": "Corps de page mis à jour"}


@router.put("/footer/about")
async def put_footer_about(
    body: FooterAboutUpdate,
    current_user: User = Depends(require_role("admin", "editor")),
    db: AsyncSession = Depends(get_db),
):
    await update_footer_about(db, body.content_json.model_dump(), current_user.id)
    return {"message": "Section À propos mise à jour"}


@router.put("/footer/contact")
async def put_footer_contact(
    body: ContactInfoUpdate,
    current_user: User = Depends(require_role("admin", "editor")),
    db: AsyncSession = Depends(get_db),
):
    await update_contact(db, body.email, body.phone, body.address, current_user.id)
    return {"message": "Contact mis à jour"}


@router.get("/footer/resources", response_model=list[ResourceLinkResponse])
async def get_resources(
    current_user: User = Depends(require_role("admin", "editor")),
    db: AsyncSession = Depends(get_db),
):
    resources = await list_resources(db)
    return [ResourceLinkResponse.model_validate(r) for r in resources]


@router.post(
    "/footer/resources",
    response_model=ResourceLinkResponse,
    status_code=201,
)
async def post_resource(
    body: ResourceLinkCreate,
    current_user: User = Depends(require_role("admin", "editor")),
    db: AsyncSession = Depends(get_db),
):
    resource = await create_resource(db, body.title, body.url, body.sort_order)
    return ResourceLinkResponse.model_validate(resource)


@router.put("/footer/resources/reorder")
async def put_reorder(
    body: ResourceReorder,
    current_user: User = Depends(require_role("admin", "editor")),
    db: AsyncSession = Depends(get_db),
):
    await reorder_resources(db, body.order)
    return {"message": "Ordre mis à jour"}


@router.put(
    "/footer/resources/{resource_id}",
    response_model=ResourceLinkResponse,
)
async def put_resource(
    resource_id: uuid.UUID,
    body: ResourceLinkUpdate,
    current_user: User = Depends(require_role("admin", "editor")),
    db: AsyncSession = Depends(get_db),
):
    resource = await update_resource(
        db, resource_id, body.title, body.url, body.sort_order
    )
    if not resource:
        raise HTTPException(status_code=404, detail="Lien non trouvé")
    return ResourceLinkResponse.model_validate(resource)


@router.delete("/footer/resources/{resource_id}", status_code=204)
async def del_resource(
    resource_id: uuid.UUID,
    current_user: User = Depends(require_role("admin", "editor")),
    db: AsyncSession = Depends(get_db),
):
    deleted = await delete_resource(db, resource_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Lien non trouvé")
