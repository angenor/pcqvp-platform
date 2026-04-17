import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.schemas.public import (
    PublicAnneesResponse,
    PublicCompteResponse,
    PublicDescriptionResponse,
    PublicDocumentsLiesResponse,
)
from app.services.public_service import (
    get_available_years,
    get_collectivite_description,
    get_parent_documents,
    get_published_compte,
)

router = APIRouter(prefix="/api/public/collectivites", tags=["public"])


@router.get("/{ctype}/{cid}/annees", response_model=PublicAnneesResponse)
async def annees(
    ctype: str,
    cid: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    if ctype not in ("province", "region", "commune"):
        raise HTTPException(status_code=404, detail="Type de collectivite invalide")

    years = await get_available_years(db, ctype, cid)
    if years is None:
        raise HTTPException(status_code=404, detail="Collectivite non trouvee")

    return {"annees": years}


@router.get("/{ctype}/{cid}/description", response_model=PublicDescriptionResponse)
async def description(
    ctype: str,
    cid: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    if ctype not in ("province", "region", "commune"):
        raise HTTPException(status_code=404, detail="Type de collectivite invalide")

    desc = await get_collectivite_description(db, ctype, cid)
    if desc is None:
        raise HTTPException(status_code=404, detail="Collectivite non trouvee")

    return desc


@router.get(
    "/{ctype}/{cid}/documents-lies",
    response_model=PublicDocumentsLiesResponse,
)
async def documents_lies(
    ctype: str,
    cid: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    if ctype not in ("province", "region", "commune"):
        raise HTTPException(status_code=404, detail="Type de collectivite invalide")

    data = await get_parent_documents(db, ctype, cid)
    if data is None:
        raise HTTPException(status_code=404, detail="Collectivite non trouvee")

    return data


@router.get("/{ctype}/{cid}/comptes", response_model=PublicCompteResponse)
async def comptes(
    ctype: str,
    cid: uuid.UUID,
    annee: int = Query(...),
    db: AsyncSession = Depends(get_db),
):
    if ctype not in ("province", "region", "commune"):
        raise HTTPException(status_code=404, detail="Type de collectivite invalide")

    data = await get_published_compte(db, ctype, cid, annee)
    if data is None:
        raise HTTPException(
            status_code=404,
            detail="Compte non trouve ou non publie",
        )

    return data


@router.get("/{ctype}/{cid}/comptes/{annee}/export")
async def export_compte(
    ctype: str,
    cid: uuid.UUID,
    annee: int,
    format: str = Query(..., pattern="^(xlsx|docx)$"),
    db: AsyncSession = Depends(get_db),
):
    if ctype not in ("province", "region", "commune"):
        raise HTTPException(status_code=404, detail="Type de collectivite invalide")

    from sqlalchemy import select

    from app.models.compte_administratif import (
        CompteAdministratif,
        CompteStatus,
        DepenseProgram,
    )

    result = await db.execute(
        select(CompteAdministratif)
        .options(
            selectinload(CompteAdministratif.depense_programs).selectinload(
                DepenseProgram.depense_lines
            ),
            selectinload(CompteAdministratif.recette_lines),
        )
        .where(
            CompteAdministratif.collectivite_type == ctype,
            CompteAdministratif.collectivite_id == cid,
            CompteAdministratif.annee_exercice == annee,
            CompteAdministratif.status == CompteStatus.published,
        )
    )
    compte = result.scalar_one_or_none()
    if not compte:
        raise HTTPException(
            status_code=404,
            detail="Compte non trouve ou non publie",
        )

    from app.services.compte_service import get_collectivite_name
    from app.services.export_service import (
        generate_excel,
        generate_word,
        sanitize_filename,
    )

    cname = await get_collectivite_name(db, ctype, cid)
    safe_name = sanitize_filename(cname or f"{ctype}_{cid}")

    if format == "xlsx":
        output = await generate_excel(db, compte)
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ext = "xlsx"
    else:
        output = await generate_word(db, compte)
        media_type = (
            "application/vnd.openxmlformats-officedocument"
            ".wordprocessingml.document"
        )
        ext = "docx"

    filename = f"Compte_Administratif_{safe_name}_{annee}.{ext}"
    return StreamingResponse(
        output,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
