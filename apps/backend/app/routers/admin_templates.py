import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_role
from app.models.user import User
from app.schemas.account_template import (
    TemplateColumnResponse,
    TemplateColumnUpdate,
    TemplateDetail,
    TemplateLineCreate,
    TemplateLineResponse,
    TemplateLineUpdate,
    TemplateListItem,
    TemplateListResponse,
)
from app.services.template_service import (
    add_line,
    delete_line,
    get_template_by_id,
    list_templates,
    update_columns,
    update_lines,
)

router = APIRouter(prefix="/api/admin", tags=["admin-templates"])


@router.get("/templates", response_model=TemplateListResponse)
async def admin_list_templates(
    current_user: User = Depends(require_role("admin", "editor")),
    db: AsyncSession = Depends(get_db),
):
    items, total = await list_templates(db)
    return TemplateListResponse(
        items=[TemplateListItem(**item) for item in items], total=total
    )


@router.get("/templates/{template_id}", response_model=TemplateDetail)
async def admin_get_template(
    template_id: uuid.UUID,
    current_user: User = Depends(require_role("admin", "editor")),
    db: AsyncSession = Depends(get_db),
):
    template = await get_template_by_id(db, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template non trouve")
    return template


@router.post(
    "/templates/{template_id}/lines",
    response_model=TemplateLineResponse,
    status_code=201,
)
async def admin_add_line(
    template_id: uuid.UUID,
    data: TemplateLineCreate,
    current_user: User = Depends(require_role("admin", "editor")),
    db: AsyncSession = Depends(get_db),
):
    result = await add_line(db, template_id, data.model_dump())
    if isinstance(result, str):
        if "non trouve" in result:
            status = 404 if "Template" in result else 422
            raise HTTPException(status_code=status, detail=result)
        if "existe deja" in result:
            raise HTTPException(status_code=409, detail=result)
        raise HTTPException(status_code=422, detail=result)
    return result


@router.delete(
    "/templates/{template_id}/lines/{line_id}",
    status_code=204,
)
async def admin_delete_line(
    template_id: uuid.UUID,
    line_id: uuid.UUID,
    current_user: User = Depends(require_role("admin", "editor")),
    db: AsyncSession = Depends(get_db),
):
    error = await delete_line(db, template_id, line_id)
    if error:
        if "non trouvee" in error:
            raise HTTPException(status_code=404, detail=error)
        raise HTTPException(status_code=409, detail=error)


@router.put(
    "/templates/{template_id}/lines",
    response_model=list[TemplateLineResponse],
)
async def admin_update_lines(
    template_id: uuid.UUID,
    data: list[TemplateLineUpdate],
    current_user: User = Depends(require_role("admin", "editor")),
    db: AsyncSession = Depends(get_db),
):
    lines_data = [d.model_dump() for d in data]
    result = await update_lines(db, template_id, lines_data)
    if isinstance(result, str):
        if "non trouve" in result:
            raise HTTPException(status_code=404, detail=result)
        raise HTTPException(status_code=422, detail=result)
    return result


@router.put(
    "/templates/{template_id}/columns",
    response_model=list[TemplateColumnResponse],
)
async def admin_update_columns(
    template_id: uuid.UUID,
    data: list[TemplateColumnUpdate],
    current_user: User = Depends(require_role("admin", "editor")),
    db: AsyncSession = Depends(get_db),
):
    cols_data = [d.model_dump() for d in data]
    result = await update_columns(db, template_id, cols_data)
    if isinstance(result, str):
        if "non trouve" in result:
            raise HTTPException(status_code=404, detail=result)
        raise HTTPException(status_code=422, detail=result)
    return result
