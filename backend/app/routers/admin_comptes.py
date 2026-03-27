import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_role
from app.models.user import User
from app.schemas.compte_administratif import (
    ChangeLogEntry,
    ChangeLogResponse,
    CompteCreate,
    CompteDetail,
    CompteListItem,
    CompteListResponse,
    CompteUpdate,
    DepenseLineResponse,
    DepenseLineUpsert,
    DepenseProgramCreate,
    DepenseProgramResponse,
    DepenseProgramUpdate,
    EquilibreResponse,
    RecapDepensesResponse,
    RecapRecettesResponse,
    RecetteLineResponse,
    RecetteLineUpsert,
    StatusResponse,
    StatusUpdate,
)
from app.services import account_service, compte_service

router = APIRouter(prefix="/api/admin/comptes", tags=["admin-comptes"])


# --- CRUD Compte ---


@router.post("", response_model=CompteDetail, status_code=201)
async def create_compte(
    data: CompteCreate,
    current_user: User = Depends(require_role("admin", "editor")),
    db: AsyncSession = Depends(get_db),
):
    result = await compte_service.create_compte(db, data.model_dump(), current_user.id)
    if isinstance(result, str):
        if "non trouvee" in result:
            raise HTTPException(status_code=404, detail=result)
        if "existe deja" in result:
            raise HTTPException(status_code=409, detail=result)
        raise HTTPException(status_code=422, detail=result)
    name = await compte_service.get_collectivite_name(
        db, result.collectivite_type.value, result.collectivite_id
    )
    return _compte_to_detail(result, name)


@router.get("", response_model=CompteListResponse)
async def list_comptes(
    collectivite_type: str | None = None,
    collectivite_id: uuid.UUID | None = None,
    annee: int | None = None,
    current_user: User = Depends(require_role("admin", "editor")),
    db: AsyncSession = Depends(get_db),
):
    items, total = await compte_service.list_comptes(
        db, collectivite_type, collectivite_id, annee
    )
    result_items = []
    for c in items:
        name = await compte_service.get_collectivite_name(
            db, c.collectivite_type.value, c.collectivite_id
        )
        result_items.append(
            CompteListItem(
                id=c.id,
                collectivite_type=c.collectivite_type.value,
                collectivite_id=c.collectivite_id,
                collectivite_name=name,
                annee_exercice=c.annee_exercice,
                status=c.status.value,
                created_by=c.created_by,
                created_at=c.created_at,
                updated_at=c.updated_at,
            )
        )
    return CompteListResponse(items=result_items, total=total)


@router.put("/{compte_id}", response_model=CompteDetail)
async def update_compte(
    compte_id: uuid.UUID,
    data: CompteUpdate,
    current_user: User = Depends(require_role("admin", "editor")),
    db: AsyncSession = Depends(get_db),
):
    update_data = data.model_dump(exclude_none=True)
    if not update_data:
        raise HTTPException(status_code=422, detail="Aucun champ a modifier")
    result = await compte_service.update_compte(
        db, compte_id, update_data, current_user.id
    )
    if isinstance(result, str):
        if "non trouvee" in result:
            raise HTTPException(status_code=404, detail=result)
        if "existe deja" in result:
            raise HTTPException(status_code=409, detail=result)
        raise HTTPException(status_code=422, detail=result)
    name = await compte_service.get_collectivite_name(
        db, result.collectivite_type.value, result.collectivite_id
    )
    return _compte_to_detail(result, name)


@router.get("/{compte_id}", response_model=CompteDetail)
async def get_compte(
    compte_id: uuid.UUID,
    current_user: User = Depends(require_role("admin", "editor")),
    db: AsyncSession = Depends(get_db),
):
    compte = await compte_service.get_compte_by_id(db, compte_id)
    if not compte:
        raise HTTPException(status_code=404, detail="Compte non trouve")
    name = await compte_service.get_collectivite_name(
        db, compte.collectivite_type.value, compte.collectivite_id
    )
    recettes = await account_service.get_recettes_with_computed(db, compte_id)
    detail = _compte_to_detail(compte, name)
    detail.recettes = recettes
    return detail


# --- Depenses computed ---


@router.get("/{compte_id}/depenses-computed")
async def get_depenses_computed(
    compte_id: uuid.UUID,
    current_user: User = Depends(require_role("admin", "editor")),
    db: AsyncSession = Depends(get_db),
):
    compte = await compte_service.get_compte_by_id(db, compte_id)
    if not compte:
        raise HTTPException(status_code=404, detail="Compte non trouve")
    return await account_service.get_depenses_with_computed(db, compte_id)


# --- Recettes ---


@router.put("/{compte_id}/recettes", response_model=RecetteLineResponse)
async def upsert_recette(
    compte_id: uuid.UUID,
    data: RecetteLineUpsert,
    current_user: User = Depends(require_role("admin", "editor")),
    db: AsyncSession = Depends(get_db),
):
    from app.services.account_service import compute_line_values

    result = await compte_service.upsert_recette_line(
        db, compte_id, data.template_line_id, data.values, current_user.id
    )
    if isinstance(result, str):
        raise HTTPException(status_code=404, detail=result)
    computed = compute_line_values(dict(result.values), "recette")
    return RecetteLineResponse(
        id=result.id,
        template_line_id=result.template_line_id,
        values=result.values,
        computed=computed,
    )


# --- Programmes ---


@router.post(
    "/{compte_id}/programmes",
    response_model=DepenseProgramResponse,
    status_code=201,
)
async def create_programme(
    compte_id: uuid.UUID,
    data: DepenseProgramCreate,
    current_user: User = Depends(require_role("admin", "editor")),
    db: AsyncSession = Depends(get_db),
):
    result = await compte_service.add_programme(
        db, compte_id, data.intitule, current_user.id
    )
    if isinstance(result, str):
        raise HTTPException(status_code=404, detail=result)
    return result


@router.put(
    "/{compte_id}/programmes/{prog_id}",
    response_model=DepenseProgramResponse,
)
async def update_programme(
    compte_id: uuid.UUID,
    prog_id: uuid.UUID,
    data: DepenseProgramUpdate,
    current_user: User = Depends(require_role("admin", "editor")),
    db: AsyncSession = Depends(get_db),
):
    result = await compte_service.update_programme(
        db, compte_id, prog_id, data.intitule, current_user.id
    )
    if isinstance(result, str):
        raise HTTPException(status_code=404, detail=result)
    return result


@router.delete("/{compte_id}/programmes/{prog_id}", status_code=204)
async def delete_programme(
    compte_id: uuid.UUID,
    prog_id: uuid.UUID,
    current_user: User = Depends(require_role("admin", "editor")),
    db: AsyncSession = Depends(get_db),
):
    error = await compte_service.delete_programme(
        db, compte_id, prog_id, current_user.id
    )
    if error:
        raise HTTPException(status_code=404, detail=error)


# --- Depenses ---


@router.put(
    "/{compte_id}/programmes/{prog_id}/depenses",
    response_model=DepenseLineResponse,
)
async def upsert_depense(
    compte_id: uuid.UUID,
    prog_id: uuid.UUID,
    data: DepenseLineUpsert,
    current_user: User = Depends(require_role("admin", "editor")),
    db: AsyncSession = Depends(get_db),
):
    from app.services.account_service import compute_line_values

    result = await compte_service.upsert_depense_line(
        db, prog_id, data.template_line_id, data.values, current_user.id
    )
    if isinstance(result, str):
        raise HTTPException(status_code=404, detail=result)
    computed = compute_line_values(dict(result.values), "depense")
    return DepenseLineResponse(
        id=result.id,
        template_line_id=result.template_line_id,
        values=result.values,
        computed=computed,
    )


# --- Status ---


@router.put("/{compte_id}/status", response_model=StatusResponse)
async def update_status(
    compte_id: uuid.UUID,
    data: StatusUpdate,
    current_user: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    result = await compte_service.update_status(
        db, compte_id, data.status, current_user.id
    )
    if isinstance(result, str):
        raise HTTPException(status_code=404, detail=result)
    return StatusResponse(
        id=result.id, status=result.status.value, updated_at=result.updated_at
    )


# --- Recapitulatifs ---


@router.get(
    "/{compte_id}/recapitulatifs/recettes",
    response_model=RecapRecettesResponse,
)
async def recap_recettes(
    compte_id: uuid.UUID,
    current_user: User = Depends(require_role("admin", "editor")),
    db: AsyncSession = Depends(get_db),
):
    compte = await compte_service.get_compte_by_id(db, compte_id)
    if not compte:
        raise HTTPException(status_code=404, detail="Compte non trouve")
    return await account_service.calculate_recettes_recap(db, compte_id)


@router.get(
    "/{compte_id}/recapitulatifs/depenses",
    response_model=RecapDepensesResponse,
)
async def recap_depenses(
    compte_id: uuid.UUID,
    current_user: User = Depends(require_role("admin", "editor")),
    db: AsyncSession = Depends(get_db),
):
    compte = await compte_service.get_compte_by_id(db, compte_id)
    if not compte:
        raise HTTPException(status_code=404, detail="Compte non trouve")
    return await account_service.calculate_depenses_recap(db, compte_id)


@router.get(
    "/{compte_id}/recapitulatifs/equilibre",
    response_model=EquilibreResponse,
)
async def equilibre(
    compte_id: uuid.UUID,
    current_user: User = Depends(require_role("admin", "editor")),
    db: AsyncSession = Depends(get_db),
):
    compte = await compte_service.get_compte_by_id(db, compte_id)
    if not compte:
        raise HTTPException(status_code=404, detail="Compte non trouve")
    return await account_service.calculate_equilibre(db, compte_id)


# --- Changelog ---


@router.get("/{compte_id}/changelog", response_model=ChangeLogResponse)
async def get_changelog(
    compte_id: uuid.UUID,
    current_user: User = Depends(require_role("admin", "editor")),
    db: AsyncSession = Depends(get_db),
):
    compte = await compte_service.get_compte_by_id(db, compte_id)
    if not compte:
        raise HTTPException(status_code=404, detail="Compte non trouve")
    items, total = await compte_service.get_changelog(db, compte_id)
    return ChangeLogResponse(
        items=[
            ChangeLogEntry(
                id=item.id,
                user_email=getattr(item, "_user_email", ""),
                change_type=item.change_type,
                detail=item.detail,
                created_at=item.created_at,
            )
            for item in items
        ],
        total=total,
    )


# --- Helpers ---


def _compte_to_detail(compte, collectivite_name: str) -> CompteDetail:
    progs = sorted(compte.depense_programs, key=lambda p: p.numero)
    return CompteDetail(
        id=compte.id,
        collectivite_type=compte.collectivite_type.value,
        collectivite_id=compte.collectivite_id,
        collectivite_name=collectivite_name,
        annee_exercice=compte.annee_exercice,
        status=compte.status.value,
        created_by=compte.created_by,
        programmes=[
            DepenseProgramResponse(
                id=p.id,
                numero=p.numero,
                intitule=p.intitule,
                created_at=p.created_at,
                updated_at=p.updated_at,
            )
            for p in progs
        ],
        created_at=compte.created_at,
        updated_at=compte.updated_at,
    )
