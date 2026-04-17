import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.compte_administratif import (
    CompteAdministratif,
    CompteStatus,
    DepenseProgram,
)
from app.models.geography import Commune, Province, Region
from app.services.account_service import (
    calculate_depenses_recap,
    calculate_equilibre,
    calculate_recettes_recap,
    get_depenses_with_computed,
    get_recettes_with_computed,
)
from app.services.collectivity_document import list_for_parent, to_read_dict
from app.services.compte_service import get_collectivite_name

MODEL_MAP = {
    "province": Province,
    "region": Region,
    "commune": Commune,
}


async def get_collectivite(
    db: AsyncSession, ctype: str, cid: uuid.UUID
) -> Province | Region | Commune | None:
    model = MODEL_MAP.get(ctype)
    if not model:
        return None
    result = await db.execute(select(model).where(model.id == cid))
    return result.scalar_one_or_none()


async def get_available_years(
    db: AsyncSession, ctype: str, cid: uuid.UUID
) -> list[int] | None:
    """Return published years for a collectivite, or None if collectivite not found."""
    entity = await get_collectivite(db, ctype, cid)
    if not entity:
        return None

    return await _get_published_years(db, ctype, cid)


async def _get_published_years(
    db: AsyncSession, ctype: str, cid: uuid.UUID
) -> list[int]:
    result = await db.execute(
        select(CompteAdministratif.annee_exercice)
        .where(
            CompteAdministratif.collectivite_type == ctype,
            CompteAdministratif.collectivite_id == cid,
            CompteAdministratif.status == CompteStatus.published,
        )
        .order_by(CompteAdministratif.annee_exercice.desc())
    )
    return list(result.scalars().all())


async def get_parent_documents(
    db: AsyncSession, ctype: str, cid: uuid.UUID
) -> dict | None:
    """Return parent collectivites with published compte years and uploaded documents.

    Skip parents that have neither published comptes nor uploaded documents.
    """
    entity = await get_collectivite(db, ctype, cid)
    if not entity:
        return None

    parents: list[dict] = []

    async def _build(ptype: str, pid: uuid.UUID, pname: str) -> dict | None:
        years = await _get_published_years(db, ptype, pid)
        docs = await list_for_parent(db, ptype, pid)
        if not years and not docs:
            return None
        return {
            "type": ptype,
            "id": pid,
            "name": pname,
            "annees": years,
            "documents": [to_read_dict(d) for d in docs],
        }

    if ctype == "commune":
        result = await db.execute(
            select(Commune)
            .options(selectinload(Commune.region).selectinload(Region.province))
            .where(Commune.id == cid)
        )
        commune = result.scalar_one_or_none()
        region = commune.region if commune else None
        if region:
            entry = await _build("region", region.id, region.name)
            if entry:
                parents.append(entry)
            province = region.province
            if province:
                entry = await _build("province", province.id, province.name)
                if entry:
                    parents.append(entry)
    elif ctype == "region":
        result = await db.execute(
            select(Region)
            .options(selectinload(Region.province))
            .where(Region.id == cid)
        )
        region = result.scalar_one_or_none()
        province = region.province if region else None
        if province:
            entry = await _build("province", province.id, province.name)
            if entry:
                parents.append(entry)

    return {"parents": parents}


async def get_collectivite_description(
    db: AsyncSession, ctype: str, cid: uuid.UUID
) -> dict | None:
    """Return collectivite name, description_json, and uploaded documents."""
    entity = await get_collectivite(db, ctype, cid)
    if not entity:
        return None

    documents = await list_for_parent(db, ctype, cid)

    return {
        "name": entity.name,
        "type": ctype,
        "description_json": entity.description_json or [],
        "banner_image": entity.banner_image,
        "documents": [to_read_dict(d) for d in documents],
    }


async def get_published_compte(
    db: AsyncSession, ctype: str, cid: uuid.UUID, annee: int
) -> dict | None:
    """Return full public data for a published compte."""
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
        return None

    collectivite_name = await get_collectivite_name(db, ctype, cid)

    # Reuse existing compute functions
    recettes_data = await get_recettes_with_computed(db, compte.id)
    depenses_data = await get_depenses_with_computed(db, compte.id)
    recap_recettes = await calculate_recettes_recap(db, compte.id)
    recap_depenses = await calculate_depenses_recap(db, compte.id)
    equilibre = await calculate_equilibre(db, compte.id)

    # Build hierarchical recettes structure (sections with nested children)
    recettes_sections = _build_hierarchical_sections(
        recettes_data["lines"], recettes_data["hierarchical_sums"]
    )

    # Build depenses by programme with hierarchical sections
    depenses_programmes = []
    for prog in depenses_data:
        prog_sections = _build_hierarchical_sections(
            prog["lines"], prog["hierarchical_sums"]
        )
        depenses_programmes.append({
            "id": prog["id"],
            "numero": prog["numero"],
            "intitule": prog["intitule"],
            "sections": prog_sections,
        })

    # Get template columns
    from app.services.account_service import _get_active_template

    recette_template = await _get_active_template(db, "recette")
    depense_template = await _get_active_template(db, "depense")

    recette_columns = []
    if recette_template:
        recette_columns = [
            {
                "code": col.code,
                "name": col.name,
                "is_computed": col.is_computed,
            }
            for col in sorted(recette_template.columns, key=lambda c: c.sort_order)
        ]

    depense_columns = []
    if depense_template:
        depense_columns = [
            {
                "code": col.code,
                "name": col.name,
                "is_computed": col.is_computed,
            }
            for col in sorted(depense_template.columns, key=lambda c: c.sort_order)
        ]

    return {
        "compte": {
            "id": str(compte.id),
            "collectivite_type": ctype,
            "collectivite_id": str(cid),
            "collectivite_name": collectivite_name,
            "annee_exercice": annee,
            "status": compte.status.value,
        },
        "recettes": {
            "template_columns": recette_columns,
            "sections": recettes_sections,
        },
        "depenses": {
            "template_columns": depense_columns,
            "programmes": depenses_programmes,
        },
        "recapitulatifs": {
            "recettes": recap_recettes,
            "depenses": recap_depenses,
        },
        "equilibre": equilibre,
    }


def _build_hierarchical_sections(
    lines: list[dict], hierarchical_sums: dict
) -> list[dict]:
    """Build hierarchical sections from flat lines with sums."""
    sections_map: dict[str, list] = {}

    # Group by section, build parent-child
    niv1_lines = [ln for ln in lines if ln["level"] == 1]
    niv2_lines = [ln for ln in lines if ln["level"] == 2]
    niv3_lines = [ln for ln in lines if ln["level"] == 3]

    for line in niv1_lines:
        sec = line["section"]
        sections_map.setdefault(sec, [])

        # Find niv2 children
        children_niv2 = [
            ln for ln in niv2_lines
            if ln.get("parent_code") == line["compte_code"]
        ]

        niv1_entry = _build_line_entry(line, hierarchical_sums)
        niv1_entry["children"] = []

        for niv2 in sorted(children_niv2, key=lambda x: x.get("sort_order", 0)):
            # Find niv3 children
            children_niv3 = [
                ln
                for ln in niv3_lines
                if ln.get("parent_code") == niv2["compte_code"]
            ]
            niv2_entry = _build_line_entry(niv2, hierarchical_sums)
            niv2_entry["children"] = [
                _build_line_entry(niv3, hierarchical_sums)
                for niv3 in sorted(
                    children_niv3, key=lambda x: x.get("sort_order", 0)
                )
            ]
            niv1_entry["children"].append(niv2_entry)

        sections_map[sec].append(niv1_entry)

    return [
        {"section": sec, "lines": section_lines}
        for sec, section_lines in sections_map.items()
    ]


def _build_line_entry(line: dict, hierarchical_sums: dict) -> dict:
    """Build a single line entry, using hierarchical sums for niv1/niv2."""
    code = line["compte_code"]
    sums = hierarchical_sums.get(code)

    values = dict(sums) if sums else dict(line.get("values", {}))
    computed = line.get("computed", {})

    if sums:
        # For aggregated lines, recompute computed from sums
        from app.services.account_service import compute_line_values

        is_recette = "or_admis" in values or "recouvrement" in values
        template_type = "recette" if is_recette else "depense"
        raw_vals = {
            k: v for k, v in values.items()
            if k not in (
                "previsions_definitives",
                "reste_a_recouvrer",
                "reste_a_payer",
                "taux_execution",
            )
        }
        computed = compute_line_values(raw_vals, template_type)

    return {
        "template_line_id": line.get("template_line_id", ""),
        "compte_code": code,
        "intitule": line["intitule"],
        "level": line["level"],
        "section": line["section"],
        "values": values,
        "computed": computed,
        "children": [],
    }
