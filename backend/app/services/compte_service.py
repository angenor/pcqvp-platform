import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.compte_administratif import (
    AccountChangeLog,
    CompteAdministratif,
    CompteStatus,
    DepenseLine,
    DepenseProgram,
    RecetteLine,
)
from app.models.geography import Commune, Province, Region

DEFAULT_PROGRAMMES = [
    "Administration et Coordination",
    "Developpement economique et social",
    "Sante",
]


async def validate_collectivite(
    db: AsyncSession, ctype: str, cid: uuid.UUID
) -> str | None:
    """Lookup collectivite by type and id. Returns name or None."""
    model_map = {
        "province": Province,
        "region": Region,
        "commune": Commune,
    }
    model = model_map.get(ctype)
    if not model:
        return None
    result = await db.execute(select(model).where(model.id == cid))
    entity = result.scalar_one_or_none()
    return entity.name if entity else None


async def create_compte(
    db: AsyncSession, data: dict, user_id: uuid.UUID
) -> CompteAdministratif | str:
    """Create a compte with 3 default programmes."""
    name = await validate_collectivite(
        db, data["collectivite_type"], data["collectivite_id"]
    )
    if name is None:
        return "Collectivite non trouvee"

    # Check uniqueness
    existing = await db.execute(
        select(CompteAdministratif).where(
            CompteAdministratif.collectivite_type == data["collectivite_type"],
            CompteAdministratif.collectivite_id == data["collectivite_id"],
            CompteAdministratif.annee_exercice == data["annee_exercice"],
        )
    )
    if existing.scalar_one_or_none():
        return "Un compte existe deja pour cette collectivite et cette annee"

    compte = CompteAdministratif(
        collectivite_type=data["collectivite_type"],
        collectivite_id=data["collectivite_id"],
        annee_exercice=data["annee_exercice"],
        created_by=user_id,
    )
    db.add(compte)
    await db.flush()

    for i, intitule in enumerate(DEFAULT_PROGRAMMES, start=1):
        prog = DepenseProgram(
            compte_admin_id=compte.id, numero=i, intitule=intitule
        )
        db.add(prog)

    await db.commit()
    await db.refresh(compte)
    return compte


async def get_compte_by_id(
    db: AsyncSession, compte_id: uuid.UUID
) -> CompteAdministratif | None:
    """Load compte with programmes and recette_lines."""
    result = await db.execute(
        select(CompteAdministratif)
        .options(
            selectinload(CompteAdministratif.depense_programs).selectinload(
                DepenseProgram.depense_lines
            ),
            selectinload(CompteAdministratif.recette_lines),
        )
        .where(CompteAdministratif.id == compte_id)
    )
    return result.scalar_one_or_none()


async def get_collectivite_name(
    db: AsyncSession, ctype: str, cid: uuid.UUID
) -> str:
    """Resolve collectivite name."""
    name = await validate_collectivite(db, ctype, cid)
    return name or "Inconnue"


# --- Recettes ---


async def upsert_recette_line(
    db: AsyncSession,
    compte_id: uuid.UUID,
    template_line_id: uuid.UUID,
    values: dict,
    user_id: uuid.UUID,
) -> RecetteLine | str:
    """Upsert a recette line. Creates changelog if compte is published."""
    compte = await get_compte_by_id(db, compte_id)
    if not compte:
        return "Compte non trouve"

    # Find existing
    result = await db.execute(
        select(RecetteLine).where(
            RecetteLine.compte_admin_id == compte_id,
            RecetteLine.template_line_id == template_line_id,
        )
    )
    line = result.scalar_one_or_none()

    old_values = dict(line.values) if line else {}

    if line:
        line.values = values
    else:
        line = RecetteLine(
            compte_admin_id=compte_id,
            template_line_id=template_line_id,
            values=values,
        )
        db.add(line)

    # Changelog if published
    if compte.status == CompteStatus.published:
        log = AccountChangeLog(
            compte_admin_id=compte_id,
            user_id=user_id,
            change_type="recette_update",
            detail={
                "template_line_id": str(template_line_id),
                "old_values": old_values,
                "new_values": values,
            },
        )
        db.add(log)

    await db.commit()
    await db.refresh(line)
    return line


# --- Programmes ---


async def add_programme(
    db: AsyncSession, compte_id: uuid.UUID, intitule: str, user_id: uuid.UUID
) -> DepenseProgram | str:
    """Add a programme with auto-incremented numero."""
    compte = await get_compte_by_id(db, compte_id)
    if not compte:
        return "Compte non trouve"

    max_num = max((p.numero for p in compte.depense_programs), default=0)
    prog = DepenseProgram(
        compte_admin_id=compte_id, numero=max_num + 1, intitule=intitule
    )
    db.add(prog)

    if compte.status == CompteStatus.published:
        await db.flush()
        log = AccountChangeLog(
            compte_admin_id=compte_id,
            user_id=user_id,
            change_type="programme_add",
            detail={
                "programme_id": str(prog.id),
                "numero": prog.numero,
                "intitule": intitule,
            },
        )
        db.add(log)

    await db.commit()
    await db.refresh(prog)
    return prog


async def update_programme(
    db: AsyncSession,
    compte_id: uuid.UUID,
    prog_id: uuid.UUID,
    intitule: str,
    user_id: uuid.UUID,
) -> DepenseProgram | str:
    """Update programme intitule."""
    result = await db.execute(
        select(DepenseProgram).where(
            DepenseProgram.id == prog_id,
            DepenseProgram.compte_admin_id == compte_id,
        )
    )
    prog = result.scalar_one_or_none()
    if not prog:
        return "Programme non trouve"

    old_intitule = prog.intitule
    prog.intitule = intitule

    # Changelog
    compte = await get_compte_by_id(db, compte_id)
    if compte and compte.status == CompteStatus.published:
        log = AccountChangeLog(
            compte_admin_id=compte_id,
            user_id=user_id,
            change_type="programme_update",
            detail={
                "programme_id": str(prog_id),
                "old_intitule": old_intitule,
                "new_intitule": intitule,
            },
        )
        db.add(log)

    await db.commit()
    await db.refresh(prog)
    return prog


async def delete_programme(
    db: AsyncSession,
    compte_id: uuid.UUID,
    prog_id: uuid.UUID,
    user_id: uuid.UUID,
) -> str | None:
    """Delete programme and cascade depense lines."""
    result = await db.execute(
        select(DepenseProgram).where(
            DepenseProgram.id == prog_id,
            DepenseProgram.compte_admin_id == compte_id,
        )
    )
    prog = result.scalar_one_or_none()
    if not prog:
        return "Programme non trouve"

    compte = await get_compte_by_id(db, compte_id)
    if compte and compte.status == CompteStatus.published:
        log = AccountChangeLog(
            compte_admin_id=compte_id,
            user_id=user_id,
            change_type="programme_delete",
            detail={
                "programme_id": str(prog_id),
                "numero": prog.numero,
                "intitule": prog.intitule,
            },
        )
        db.add(log)

    await db.delete(prog)
    await db.commit()
    return None


# --- Depenses ---


async def upsert_depense_line(
    db: AsyncSession,
    programme_id: uuid.UUID,
    template_line_id: uuid.UUID,
    values: dict,
    user_id: uuid.UUID,
) -> DepenseLine | str:
    """Upsert a depense line."""
    result = await db.execute(
        select(DepenseProgram).where(DepenseProgram.id == programme_id)
    )
    prog = result.scalar_one_or_none()
    if not prog:
        return "Programme non trouve"

    result = await db.execute(
        select(DepenseLine).where(
            DepenseLine.programme_id == programme_id,
            DepenseLine.template_line_id == template_line_id,
        )
    )
    line = result.scalar_one_or_none()
    old_values = dict(line.values) if line else {}

    if line:
        line.values = values
    else:
        line = DepenseLine(
            programme_id=programme_id,
            template_line_id=template_line_id,
            values=values,
        )
        db.add(line)

    # Changelog if published
    compte = await get_compte_by_id(db, prog.compte_admin_id)
    if compte and compte.status == CompteStatus.published:
        log = AccountChangeLog(
            compte_admin_id=prog.compte_admin_id,
            user_id=user_id,
            change_type="depense_update",
            detail={
                "programme_id": str(programme_id),
                "template_line_id": str(template_line_id),
                "old_values": old_values,
                "new_values": values,
            },
        )
        db.add(log)

    await db.commit()
    await db.refresh(line)
    return line


# --- Status ---


async def update_status(
    db: AsyncSession,
    compte_id: uuid.UUID,
    new_status: str,
    user_id: uuid.UUID,
) -> CompteAdministratif | str:
    """Change compte status and log."""
    compte = await get_compte_by_id(db, compte_id)
    if not compte:
        return "Compte non trouve"

    old_status = compte.status.value
    compte.status = new_status

    log = AccountChangeLog(
        compte_admin_id=compte_id,
        user_id=user_id,
        change_type="status_change",
        detail={"old_status": old_status, "new_status": new_status},
    )
    db.add(log)

    await db.commit()
    await db.refresh(compte)
    return compte


# --- List ---


async def list_comptes(
    db: AsyncSession,
    collectivite_type: str | None = None,
    collectivite_id: uuid.UUID | None = None,
    annee: int | None = None,
) -> tuple[list[CompteAdministratif], int]:
    """List comptes with optional filters."""
    query = select(CompteAdministratif).order_by(
        CompteAdministratif.annee_exercice.desc(),
        CompteAdministratif.created_at.desc(),
    )
    count_query = select(func.count()).select_from(CompteAdministratif)

    if collectivite_type:
        query = query.where(
            CompteAdministratif.collectivite_type == collectivite_type
        )
        count_query = count_query.where(
            CompteAdministratif.collectivite_type == collectivite_type
        )
    if collectivite_id:
        query = query.where(
            CompteAdministratif.collectivite_id == collectivite_id
        )
        count_query = count_query.where(
            CompteAdministratif.collectivite_id == collectivite_id
        )
    if annee:
        query = query.where(CompteAdministratif.annee_exercice == annee)
        count_query = count_query.where(
            CompteAdministratif.annee_exercice == annee
        )

    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    result = await db.execute(query)
    items = list(result.scalars().all())

    return items, total


# --- Changelog ---


async def get_changelog(
    db: AsyncSession, compte_id: uuid.UUID
) -> tuple[list[AccountChangeLog], int]:
    """Get changelog entries for a compte."""
    from app.models.user import User

    query = (
        select(AccountChangeLog)
        .where(AccountChangeLog.compte_admin_id == compte_id)
        .order_by(AccountChangeLog.created_at.desc())
    )
    result = await db.execute(query)
    items = list(result.scalars().all())

    # Resolve user emails
    for item in items:
        user_result = await db.execute(
            select(User.email).where(User.id == item.user_id)
        )
        item._user_email = user_result.scalar_one_or_none() or "unknown"

    return items, len(items)
