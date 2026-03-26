import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.account_template import (
    AccountTemplate,
    AccountTemplateColumn,
    AccountTemplateLine,
)

# --- Read ---


async def list_templates(
    db: AsyncSession,
) -> tuple[list[dict], int]:
    """Liste tous les templates avec le nombre de lignes et colonnes."""
    result = await db.execute(
        select(AccountTemplate).order_by(AccountTemplate.name)
    )
    templates = list(result.scalars().all())

    items = []
    for t in templates:
        lines_count = await db.execute(
            select(func.count())
            .select_from(AccountTemplateLine)
            .where(AccountTemplateLine.template_id == t.id)
        )
        cols_count = await db.execute(
            select(func.count())
            .select_from(AccountTemplateColumn)
            .where(AccountTemplateColumn.template_id == t.id)
        )
        items.append(
            {
                "id": t.id,
                "name": t.name,
                "type": t.type.value,
                "version": t.version,
                "is_active": t.is_active,
                "lines_count": lines_count.scalar_one(),
                "columns_count": cols_count.scalar_one(),
                "created_at": t.created_at,
            }
        )

    return items, len(items)


async def get_template_by_id(
    db: AsyncSession, template_id: uuid.UUID
) -> AccountTemplate | None:
    """Recupere un template avec ses lignes et colonnes."""
    result = await db.execute(
        select(AccountTemplate)
        .options(
            selectinload(AccountTemplate.lines),
            selectinload(AccountTemplate.columns),
        )
        .where(AccountTemplate.id == template_id)
    )
    template = result.scalar_one_or_none()
    if template:
        template.lines = sorted(template.lines, key=lambda x: x.sort_order)
        template.columns = sorted(template.columns, key=lambda c: c.sort_order)
    return template


# --- Write ---


async def add_line(
    db: AsyncSession,
    template_id: uuid.UUID,
    line_data: dict,
) -> AccountTemplateLine | str:
    """Ajoute une ligne au template. Retourne la ligne ou un message d'erreur."""
    template = await get_template_by_id(db, template_id)
    if template is None:
        return "Template non trouve"

    # Check duplicate code
    existing_codes = {line.compte_code for line in template.lines}
    if line_data["compte_code"] in existing_codes:
        return f"Code {line_data['compte_code']} existe deja dans ce template"

    # Check parent exists if level > 1
    if line_data.get("parent_code"):
        parent_exists = any(
            ln.compte_code == line_data["parent_code"]
            for ln in template.lines
        )
        if not parent_exists:
            return f"Parent {line_data['parent_code']} non trouve dans le template"

    line = AccountTemplateLine(template_id=template_id, **line_data)
    db.add(line)
    await db.commit()
    await db.refresh(line)
    return line


async def delete_line(
    db: AsyncSession,
    template_id: uuid.UUID,
    line_id: uuid.UUID,
) -> str | None:
    """Supprime une ligne. Retourne un message d'erreur si elle a des enfants."""
    result = await db.execute(
        select(AccountTemplateLine).where(
            AccountTemplateLine.id == line_id,
            AccountTemplateLine.template_id == template_id,
        )
    )
    line = result.scalar_one_or_none()
    if line is None:
        return "Ligne non trouvee"

    # Check for children
    children = await db.execute(
        select(func.count())
        .select_from(AccountTemplateLine)
        .where(
            AccountTemplateLine.template_id == template_id,
            AccountTemplateLine.parent_code == line.compte_code,
        )
    )
    if children.scalar_one() > 0:
        return "Impossible de supprimer : cette ligne a des enfants"

    await db.delete(line)
    await db.commit()
    return None


async def update_lines(
    db: AsyncSession,
    template_id: uuid.UUID,
    lines_data: list[dict],
) -> list[AccountTemplateLine] | str:
    """Met a jour les lignes d'un template (bulk)."""
    template = await get_template_by_id(db, template_id)
    if template is None:
        return "Template non trouve"

    # Check for duplicate codes
    codes = [ld["compte_code"] for ld in lines_data]
    if len(codes) != len(set(codes)):
        dupes = [c for c in codes if codes.count(c) > 1]
        return f"Code {dupes[0]} duplique"

    lines_by_id = {ln.id: ln for ln in template.lines}
    for ld in lines_data:
        line_id = ld.get("id")
        if line_id and line_id in lines_by_id:
            line = lines_by_id[line_id]
            line.compte_code = ld["compte_code"]
            line.intitule = ld["intitule"]
            line.level = ld["level"]
            line.parent_code = ld.get("parent_code")
            line.section = ld["section"]
            line.sort_order = ld["sort_order"]

    await db.commit()

    # Re-fetch sorted
    template = await get_template_by_id(db, template_id)
    return template.lines


async def update_columns(
    db: AsyncSession,
    template_id: uuid.UUID,
    columns_data: list[dict],
) -> list[AccountTemplateColumn] | str:
    """Met a jour les colonnes d'un template (bulk)."""
    template = await get_template_by_id(db, template_id)
    if template is None:
        return "Template non trouve"

    # Check for duplicate codes
    codes = [cd["code"] for cd in columns_data]
    if len(codes) != len(set(codes)):
        dupes = [c for c in codes if codes.count(c) > 1]
        return f"Code {dupes[0]} duplique"

    cols_by_id = {c.id: c for c in template.columns}
    for cd in columns_data:
        col_id = cd.get("id")
        if col_id and col_id in cols_by_id:
            col = cols_by_id[col_id]
            col.name = cd["name"]
            col.code = cd["code"]
            col.data_type = cd["data_type"]
            col.is_computed = cd["is_computed"]
            col.formula = cd.get("formula")
            col.sort_order = cd["sort_order"]

    await db.commit()

    template = await get_template_by_id(db, template_id)
    return template.columns
