import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_role
from app.models.user import User
from app.schemas.collectivity_document import (
    CollectivityDocumentCreate,
    CollectivityDocumentFileReplace,
    CollectivityDocumentRead,
    CollectivityDocumentsReorder,
    CollectivityDocumentUpdate,
    ParentType,
)
from app.services import collectivity_document as service

router = APIRouter(
    prefix="/api/admin/collectivity-documents",
    tags=["admin-collectivity-documents"],
)


@router.get("", response_model=list[CollectivityDocumentRead])
async def list_documents(
    parent_type: ParentType,
    parent_id: uuid.UUID,
    current_user: User = Depends(require_role("admin", "editor")),
    db: AsyncSession = Depends(get_db),
):
    if not await service.parent_exists(db, parent_type, parent_id):
        raise HTTPException(status_code=404, detail="Parent non trouve")
    docs = await service.list_for_parent(db, parent_type, parent_id)
    return [service.to_read_dict(d) for d in docs]


@router.post("", response_model=CollectivityDocumentRead, status_code=201)
async def create_document(
    data: CollectivityDocumentCreate,
    current_user: User = Depends(require_role("admin", "editor")),
    db: AsyncSession = Depends(get_db),
):
    if not await service.parent_exists(db, data.parent_type, data.parent_id):
        raise HTTPException(status_code=404, detail="Parent non trouve")
    doc = await service.create(
        db,
        parent_type=data.parent_type,
        parent_id=data.parent_id,
        title=data.title,
        file_path=data.file_path,
        file_mime=data.file_mime,
        file_size_bytes=data.file_size_bytes,
    )
    return service.to_read_dict(doc)


@router.patch("/reorder", response_model=list[CollectivityDocumentRead])
async def reorder_documents(
    data: CollectivityDocumentsReorder,
    current_user: User = Depends(require_role("admin", "editor")),
    db: AsyncSession = Depends(get_db),
):
    if not await service.parent_exists(db, data.parent_type, data.parent_id):
        raise HTTPException(status_code=404, detail="Parent non trouve")
    result = await service.reorder(
        db, data.parent_type, data.parent_id, data.ordered_ids
    )
    if isinstance(result, str):
        raise HTTPException(status_code=400, detail=result)
    return [service.to_read_dict(d) for d in result]


@router.put("/{doc_id}", response_model=CollectivityDocumentRead)
async def update_document(
    doc_id: uuid.UUID,
    data: CollectivityDocumentUpdate,
    current_user: User = Depends(require_role("admin", "editor")),
    db: AsyncSession = Depends(get_db),
):
    doc = await service.get_by_id(db, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document non trouve")
    updated = await service.update_title(db, doc, data.title)
    return service.to_read_dict(updated)


@router.put("/{doc_id}/file", response_model=CollectivityDocumentRead)
async def replace_document_file(
    doc_id: uuid.UUID,
    data: CollectivityDocumentFileReplace,
    current_user: User = Depends(require_role("admin", "editor")),
    db: AsyncSession = Depends(get_db),
):
    doc = await service.get_by_id(db, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document non trouve")
    updated = await service.replace_file(
        db,
        doc,
        file_path=data.file_path,
        file_mime=data.file_mime,
        file_size_bytes=data.file_size_bytes,
    )
    return service.to_read_dict(updated)


@router.delete("/{doc_id}", status_code=204)
async def delete_document(
    doc_id: uuid.UUID,
    current_user: User = Depends(require_role("admin", "editor")),
    db: AsyncSession = Depends(get_db),
):
    doc = await service.get_by_id(db, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document non trouve")
    await service.delete(db, doc)
