import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.editorial import ContactInfo, EditorialContent, ResourceLink

# --- Utility ---


async def get_or_create_content(
    db: AsyncSession, section_key: str
) -> EditorialContent:
    result = await db.execute(
        select(EditorialContent).where(
            EditorialContent.section_key == section_key
        )
    )
    content = result.scalar_one_or_none()
    if not content:
        content = EditorialContent(section_key=section_key)
        db.add(content)
        await db.flush()
    return content


async def get_or_create_contact(db: AsyncSession) -> ContactInfo:
    result = await db.execute(select(ContactInfo))
    contact = result.scalar_one_or_none()
    if not contact:
        contact = ContactInfo()
        db.add(contact)
        await db.flush()
    return contact


# --- Hero ---


async def get_hero(db: AsyncSession) -> dict:
    keys = ["hero_title", "hero_subtitle", "hero_description"]
    result = await db.execute(
        select(EditorialContent).where(
            EditorialContent.section_key.in_(keys)
        )
    )
    rows = {r.section_key: r for r in result.scalars().all()}
    return {
        "title": rows.get("hero_title"),
        "subtitle": rows.get("hero_subtitle"),
        "description": rows.get("hero_description"),
    }


async def update_hero(
    db: AsyncSession,
    title: str,
    subtitle: str | None,
    description: str | None,
    user_id: uuid.UUID,
) -> None:
    fields = {
        "hero_title": title,
        "hero_subtitle": subtitle or "",
        "hero_description": description or "",
    }
    for key, value in fields.items():
        content = await get_or_create_content(db, key)
        content.content_text = value
        content.updated_by = user_id
    await db.commit()


# --- Body ---


async def get_body(db: AsyncSession) -> EditorialContent | None:
    result = await db.execute(
        select(EditorialContent).where(
            EditorialContent.section_key == "body_content"
        )
    )
    return result.scalar_one_or_none()


async def update_body(
    db: AsyncSession, content_json: dict, user_id: uuid.UUID
) -> None:
    content = await get_or_create_content(db, "body_content")
    content.content_json = content_json
    content.updated_by = user_id
    await db.commit()


# --- Footer About ---


async def get_footer_about(db: AsyncSession) -> EditorialContent | None:
    result = await db.execute(
        select(EditorialContent).where(
            EditorialContent.section_key == "footer_about"
        )
    )
    return result.scalar_one_or_none()


async def update_footer_about(
    db: AsyncSession, content_json: dict, user_id: uuid.UUID
) -> None:
    content = await get_or_create_content(db, "footer_about")
    content.content_json = content_json
    content.updated_by = user_id
    await db.commit()


# --- Contact ---


async def get_contact(db: AsyncSession) -> ContactInfo | None:
    result = await db.execute(select(ContactInfo))
    return result.scalar_one_or_none()


async def update_contact(
    db: AsyncSession,
    email: str | None,
    phone: str | None,
    address: str | None,
    user_id: uuid.UUID,
) -> None:
    contact = await get_or_create_contact(db)
    contact.email = email
    contact.phone = phone
    contact.address = address
    contact.updated_by = user_id
    await db.commit()


# --- Resources ---


async def list_resources(db: AsyncSession) -> list[ResourceLink]:
    result = await db.execute(
        select(ResourceLink).order_by(ResourceLink.sort_order)
    )
    return list(result.scalars().all())


async def create_resource(
    db: AsyncSession, title: str, url: str, sort_order: int
) -> ResourceLink:
    resource = ResourceLink(title=title, url=url, sort_order=sort_order)
    db.add(resource)
    await db.commit()
    await db.refresh(resource)
    return resource


async def update_resource(
    db: AsyncSession,
    resource_id: uuid.UUID,
    title: str | None,
    url: str | None,
    sort_order: int | None,
) -> ResourceLink | None:
    result = await db.execute(
        select(ResourceLink).where(ResourceLink.id == resource_id)
    )
    resource = result.scalar_one_or_none()
    if not resource:
        return None
    if title is not None:
        resource.title = title
    if url is not None:
        resource.url = url
    if sort_order is not None:
        resource.sort_order = sort_order
    await db.commit()
    await db.refresh(resource)
    return resource


async def delete_resource(
    db: AsyncSession, resource_id: uuid.UUID
) -> bool:
    result = await db.execute(
        select(ResourceLink).where(ResourceLink.id == resource_id)
    )
    resource = result.scalar_one_or_none()
    if not resource:
        return False
    await db.delete(resource)
    await db.commit()
    return True


async def reorder_resources(
    db: AsyncSession, order: list[uuid.UUID]
) -> None:
    for idx, resource_id in enumerate(order):
        result = await db.execute(
            select(ResourceLink).where(ResourceLink.id == resource_id)
        )
        resource = result.scalar_one_or_none()
        if resource:
            resource.sort_order = idx
    await db.commit()
