import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.account_template import (
    AccountTemplate,
    AccountTemplateLine,
)
from app.models.compte_administratif import (
    DepenseProgram,
    RecetteLine,
)


def compute_line_values(values: dict, template_type: str) -> dict:
    """Compute derived columns for a line."""
    bp = values.get("budget_primitif", 0) or 0
    ba = values.get("budget_additionnel", 0) or 0
    mods = values.get("modifications", 0) or 0
    prev_def = bp + ba + mods

    computed = {"previsions_definitives": prev_def}

    if template_type == "recette":
        or_admis = values.get("or_admis", 0) or 0
        recouvrement = values.get("recouvrement", 0) or 0
        computed["reste_a_recouvrer"] = or_admis - recouvrement
        computed["taux_execution"] = (
            round(or_admis / prev_def, 4) if prev_def else None
        )
    else:
        mandat = values.get("mandat_admis", 0) or 0
        paiement = values.get("paiement", 0) or 0
        computed["reste_a_payer"] = mandat - paiement
        computed["taux_execution"] = (
            round(mandat / prev_def, 4) if prev_def else None
        )

    return computed


def compute_hierarchical_sums(
    lines_data: list[dict], template_lines: list[AccountTemplateLine]
) -> dict[str, dict[str, int]]:
    """Compute Niv1 and Niv2 sums from Niv3 data."""
    tl_map = {str(tl.id): tl for tl in template_lines}

    # Index values by template_line_id
    values_by_code: dict[str, dict] = {}
    for ld in lines_data:
        tl_id = str(ld.get("template_line_id", ""))
        tl = tl_map.get(tl_id)
        if tl and tl.level == 3:
            values_by_code[tl.compte_code] = ld.get("values", {})

    sums: dict[str, dict[str, int]] = {}

    # Sum Niv3 → Niv2
    for tl in template_lines:
        if tl.level == 2:
            children = [
                t for t in template_lines
                if t.level == 3 and t.parent_code == tl.compte_code
            ]
            agg: dict[str, int] = {}
            for child in children:
                child_vals = values_by_code.get(child.compte_code, {})
                for key, val in child_vals.items():
                    agg[key] = agg.get(key, 0) + (val or 0)
            # Add computed
            comp = compute_line_values(agg, "recette")
            agg.update(comp)
            sums[tl.compte_code] = agg

    # Sum Niv2 → Niv1
    for tl in template_lines:
        if tl.level == 1:
            children = [
                t for t in template_lines
                if t.level == 2 and t.parent_code == tl.compte_code
            ]
            agg: dict[str, int] = {}
            for child in children:
                child_sums = sums.get(child.compte_code, {})
                for key, val in child_sums.items():
                    if key != "taux_execution":
                        agg[key] = agg.get(key, 0) + (val or 0)
            sums[tl.compte_code] = agg

    return sums


async def _get_active_template(
    db: AsyncSession, ttype: str
) -> AccountTemplate | None:
    """Fetch active template of given type with lines."""
    result = await db.execute(
        select(AccountTemplate)
        .options(selectinload(AccountTemplate.lines))
        .where(
            AccountTemplate.type == ttype,
            AccountTemplate.is_active.is_(True),
        )
    )
    template = result.scalar_one_or_none()
    if template:
        template.lines = sorted(template.lines, key=lambda x: x.sort_order)
    return template


async def get_recettes_with_computed(
    db: AsyncSession, compte_id: uuid.UUID
) -> dict:
    """Load recette lines and compute values + hierarchical sums."""
    template = await _get_active_template(db, "recette")
    if not template:
        return {"lines": [], "hierarchical_sums": {}}

    result = await db.execute(
        select(RecetteLine).where(RecetteLine.compte_admin_id == compte_id)
    )
    recette_lines = list(result.scalars().all())
    values_by_tl = {str(rl.template_line_id): rl for rl in recette_lines}

    lines_output = []
    lines_for_sums = []
    for tl in template.lines:
        rl = values_by_tl.get(str(tl.id))
        vals = dict(rl.values) if rl else {}
        computed = compute_line_values(vals, "recette")
        line_data = {
            "template_line_id": str(tl.id),
            "compte_code": tl.compte_code,
            "intitule": tl.intitule,
            "level": tl.level,
            "parent_code": tl.parent_code,
            "section": tl.section.value,
            "sort_order": tl.sort_order,
            "values": vals,
            "computed": computed,
        }
        if rl:
            line_data["id"] = str(rl.id)
        lines_output.append(line_data)
        lines_for_sums.append(
            {"template_line_id": str(tl.id), "values": vals}
        )

    hierarchical_sums = compute_hierarchical_sums(lines_for_sums, template.lines)

    return {"lines": lines_output, "hierarchical_sums": hierarchical_sums}


async def get_depenses_with_computed(
    db: AsyncSession, compte_id: uuid.UUID
) -> list[dict]:
    """Load depense programmes with lines and computed values."""
    template = await _get_active_template(db, "depense")
    if not template:
        return []


    result = await db.execute(
        select(DepenseProgram)
        .options(selectinload(DepenseProgram.depense_lines))
        .where(DepenseProgram.compte_admin_id == compte_id)
        .order_by(DepenseProgram.numero)
    )
    programmes = list(result.scalars().all())

    programmes_output = []
    for prog in programmes:
        values_by_tl = {str(dl.template_line_id): dl for dl in prog.depense_lines}

        lines_output = []
        lines_for_sums = []
        for tl in template.lines:
            dl = values_by_tl.get(str(tl.id))
            vals = dict(dl.values) if dl else {}
            computed = compute_line_values(vals, "depense")
            line_data = {
                "template_line_id": str(tl.id),
                "compte_code": tl.compte_code,
                "intitule": tl.intitule,
                "level": tl.level,
                "parent_code": tl.parent_code,
                "section": tl.section.value,
                "sort_order": tl.sort_order,
                "values": vals,
                "computed": computed,
            }
            if dl:
                line_data["id"] = str(dl.id)
            lines_output.append(line_data)
            lines_for_sums.append(
                {"template_line_id": str(tl.id), "values": vals}
            )

        h_sums = compute_hierarchical_sums(lines_for_sums, template.lines)

        programmes_output.append({
            "id": str(prog.id),
            "numero": prog.numero,
            "intitule": prog.intitule,
            "lines": lines_output,
            "hierarchical_sums": h_sums,
        })

    return programmes_output


# --- Recapitulatifs ---


async def calculate_recettes_recap(
    db: AsyncSession, compte_id: uuid.UUID
) -> dict:
    """Aggregate recettes by Niv1 category, grouped by section."""
    template = await _get_active_template(db, "recette")
    if not template:
        return {"sections": []}

    result = await db.execute(
        select(RecetteLine).where(RecetteLine.compte_admin_id == compte_id)
    )
    recette_lines = list(result.scalars().all())
    values_by_tl = {str(rl.template_line_id): rl for rl in recette_lines}

    # Build Niv3 values by code
    code_vals: dict[str, dict] = {}
    for tl in template.lines:
        if tl.level == 3:
            rl = values_by_tl.get(str(tl.id))
            code_vals[tl.compte_code] = dict(rl.values) if rl else {}

    # Aggregate Niv3 → Niv2 → Niv1
    niv1_sums: dict[str, dict] = {}
    for tl in template.lines:
        if tl.level == 1:
            niv2_children = [
                t for t in template.lines
                if t.level == 2 and t.parent_code == tl.compte_code
            ]
            agg: dict[str, int] = {}
            for niv2 in niv2_children:
                niv3_children = [
                    t for t in template.lines
                    if t.level == 3
                    and t.parent_code == niv2.compte_code
                ]
                for niv3 in niv3_children:
                    for key, val in code_vals.get(niv3.compte_code, {}).items():
                        agg[key] = agg.get(key, 0) + (val or 0)
            comp = compute_line_values(agg, "recette")
            agg.update(comp)
            niv1_sums[tl.compte_code] = agg

    # Group by section, separate reelles/ordre
    sections_map: dict[str, dict] = {}
    niv1_lines = [t for t in template.lines if t.level == 1]
    niv1_by_section: dict[str, list] = {}
    for tl in niv1_lines:
        sec = tl.section.value
        niv1_by_section.setdefault(sec, []).append(tl)

    for sec_name, niv1s in niv1_by_section.items():
        categories = []
        for tl in sorted(niv1s, key=lambda x: x.sort_order):
            s = niv1_sums.get(tl.compte_code, {})
            categories.append({
                "compte_code": tl.compte_code,
                "intitule": tl.intitule,
                "previsions_definitives": s.get("previsions_definitives", 0),
                "or_admis": s.get("or_admis", 0),
                "recouvrement": s.get("recouvrement", 0),
                "reste_a_recouvrer": s.get("reste_a_recouvrer", 0),
            })

        total_keys = [
            "previsions_definitives",
            "or_admis",
            "recouvrement",
            "reste_a_recouvrer",
        ]
        total_section = {k: sum(c.get(k, 0) for c in categories) for k in total_keys}

        sections_map[sec_name] = {
            "section": sec_name,
            "categories": categories,
            "total_reelles": total_section,
            "total_ordre": {k: 0 for k in total_keys},
            "total_section": total_section,
        }

    return {"sections": list(sections_map.values())}


async def calculate_depenses_recap(
    db: AsyncSession, compte_id: uuid.UUID
) -> dict:
    """Cross-tab categories x programmes with mandat/paiement/reste."""
    template = await _get_active_template(db, "depense")
    if not template:
        return {"sections": [], "programmes": []}

    result = await db.execute(
        select(DepenseProgram)
        .options(selectinload(DepenseProgram.depense_lines))
        .where(DepenseProgram.compte_admin_id == compte_id)
        .order_by(DepenseProgram.numero)
    )
    programmes = list(result.scalars().all())

    # Build per-programme, per-niv1 sums
    niv1_lines = [t for t in template.lines if t.level == 1]

    def _niv1_sum_for_prog(prog: DepenseProgram, niv1_code: str) -> dict:
        values_by_tl = {str(dl.template_line_id): dl for dl in prog.depense_lines}
        niv2s = [
            t for t in template.lines
            if t.level == 2 and t.parent_code == niv1_code
        ]
        total = {"mandat_admis": 0, "paiement": 0, "reste_a_payer": 0}
        for niv2 in niv2s:
            niv3s = [
                t for t in template.lines
                if t.level == 3
                and t.parent_code == niv2.compte_code
            ]
            for niv3 in niv3s:
                dl = values_by_tl.get(str(niv3.id))
                if dl:
                    v = dl.values
                    total["mandat_admis"] += v.get("mandat_admis", 0) or 0
                    total["paiement"] += v.get("paiement", 0) or 0
        total["reste_a_payer"] = total["mandat_admis"] - total["paiement"]
        return total

    # Group by section
    sections_map: dict[str, list] = {}
    for tl in niv1_lines:
        sec = tl.section.value
        sections_map.setdefault(sec, []).append(tl)

    sections_output = []
    for sec_name, niv1s in sections_map.items():
        categories = []
        sec_total = {"mandat_admis": 0, "paiement": 0, "reste_a_payer": 0}

        for tl in sorted(niv1s, key=lambda x: x.sort_order):
            progs_data = []
            cat_total = {"mandat_admis": 0, "paiement": 0, "reste_a_payer": 0}
            for prog in programmes:
                ps = _niv1_sum_for_prog(prog, tl.compte_code)
                progs_data.append({
                    "programme_id": str(prog.id),
                    "numero": prog.numero,
                    **ps,
                })
                for k in cat_total:
                    cat_total[k] += ps[k]

            categories.append({
                "compte_code": tl.compte_code,
                "intitule": tl.intitule,
                "programmes": progs_data,
                "total": cat_total,
            })
            for k in sec_total:
                sec_total[k] += cat_total[k]

        sections_output.append({
            "section": sec_name,
            "categories": categories,
            "total_section": sec_total,
        })

    progs_response = [
        {
            "id": str(p.id),
            "numero": p.numero,
            "intitule": p.intitule,
            "created_at": p.created_at.isoformat(),
        }
        for p in programmes
    ]

    return {"sections": sections_output, "programmes": progs_response}


async def calculate_equilibre(
    db: AsyncSession, compte_id: uuid.UUID
) -> dict:
    """Balance recettes vs depenses by section."""
    recap_r = await calculate_recettes_recap(db, compte_id)
    recap_d = await calculate_depenses_recap(db, compte_id)

    def _build_side(recap_sections: list, sec_name: str, value_key: str) -> dict:
        section = next((s for s in recap_sections if s["section"] == sec_name), None)
        if not section:
            return {
                "reelles": [],
                "total_reelles": 0,
                "ordre": [],
                "total_ordre": 0,
                "total": 0,
            }

        reelles = []
        for cat in section.get("categories", []):
            montant = cat.get(value_key, 0)
            reelles.append({
                "compte_code": cat["compte_code"],
                "intitule": cat["intitule"],
                "montant": montant,
            })

        total = sum(r["montant"] for r in reelles)
        return {
            "reelles": reelles,
            "total_reelles": total,
            "ordre": [],
            "total_ordre": 0,
            "total": total,
        }

    def _build_dep_side(recap_sections: list, sec_name: str) -> dict:
        section = next((s for s in recap_sections if s["section"] == sec_name), None)
        if not section:
            return {
                "reelles": [],
                "total_reelles": 0,
                "ordre": [],
                "total_ordre": 0,
                "total": 0,
            }

        reelles = []
        for cat in section.get("categories", []):
            montant = cat.get("total", {}).get("mandat_admis", 0)
            reelles.append({
                "compte_code": cat["compte_code"],
                "intitule": cat["intitule"],
                "montant": montant,
            })

        total = sum(r["montant"] for r in reelles)
        return {
            "reelles": reelles,
            "total_reelles": total,
            "ordre": [],
            "total_ordre": 0,
            "total": total,
        }

    fonc_recettes = _build_side(recap_r["sections"], "fonctionnement", "or_admis")
    fonc_depenses = _build_dep_side(recap_d["sections"], "fonctionnement")
    inv_recettes = _build_side(recap_r["sections"], "investissement", "or_admis")
    inv_depenses = _build_dep_side(recap_d["sections"], "investissement")

    fonc_excedent = fonc_recettes["total"] - fonc_depenses["total"]
    inv_excedent = inv_recettes["total"] - inv_depenses["total"]

    return {
        "fonctionnement": {
            "depenses": fonc_depenses,
            "recettes": fonc_recettes,
            "excedent": fonc_excedent,
        },
        "investissement": {
            "depenses": inv_depenses,
            "recettes": inv_recettes,
            "excedent": inv_excedent,
        },
        "resultat_definitif": fonc_excedent + inv_excedent,
    }
