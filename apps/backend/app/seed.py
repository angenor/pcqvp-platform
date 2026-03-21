"""Seed complet : admin + templates + compte administratif Andrafiabe 2023.

Usage:
    cd apps/backend && python -m app.seed
"""

import asyncio

from sqlalchemy import select

from app.core.config import get_settings
from app.core.database import async_session
from app.core.security import hash_password
from app.models.account_template import AccountTemplate, AccountTemplateLine, TemplateType
from app.models.compte_administratif import (
    CollectiviteType,
    CompteAdministratif,
    CompteStatus,
    DepenseLine,
    DepenseProgram,
    RecetteLine,
)
from app.models.geography import Commune, Province, Region
from app.models.user import User, UserRole
from app.services.seed_templates import (
    PROGRAMME_SHEETS,
    parse_andrafiabe_depenses,
    parse_andrafiabe_recettes,
    seed_templates,
)


async def seed_admin(db) -> User:
    """Create admin user if not exists, return it."""
    settings = get_settings()
    email = settings.FIRST_ADMIN_EMAIL.lower()
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if user:
        print(f"Admin {email} already exists.")
        return user

    user = User(
        email=email,
        hashed_password=hash_password(settings.FIRST_ADMIN_PASSWORD),
        role=UserRole.admin,
    )
    db.add(user)
    await db.flush()
    print(f"Admin {email} created.")
    return user


async def seed_geography(db) -> Commune:
    """Create Antsiranana > Diana > Andrafiabe if not exists."""
    # Province
    result = await db.execute(
        select(Province).where(Province.code == "PRV-ANTSIRANANA")
    )
    province = result.scalar_one_or_none()
    if not province:
        province = Province(name="Antsiranana", code="PRV-ANTSIRANANA")
        db.add(province)
        await db.flush()
        print("Province Antsiranana created.")

    # Region
    result = await db.execute(
        select(Region).where(Region.code == "REG-DIANA")
    )
    region = result.scalar_one_or_none()
    if not region:
        region = Region(
            name="Diana", code="REG-DIANA", province_id=province.id
        )
        db.add(region)
        await db.flush()
        print("Region Diana created.")

    # Commune
    result = await db.execute(
        select(Commune).where(Commune.code == "COM-ANDRAFIABE")
    )
    commune = result.scalar_one_or_none()
    if not commune:
        commune = Commune(
            name="Andrafiabe", code="COM-ANDRAFIABE", region_id=region.id
        )
        db.add(commune)
        await db.flush()
        print("Commune Andrafiabe created.")

    return commune


async def seed_compte_andrafiabe(db, commune: Commune, admin: User) -> None:
    """Create CompteAdministratif for Andrafiabe 2023 with parsed data."""
    # Check if already exists
    result = await db.execute(
        select(CompteAdministratif).where(
            CompteAdministratif.collectivite_type == CollectiviteType.commune,
            CompteAdministratif.collectivite_id == commune.id,
            CompteAdministratif.annee_exercice == 2023,
        )
    )
    if result.scalar_one_or_none():
        print("Compte Andrafiabe 2023 already exists.")
        return

    # Load template lines (recettes + depenses)
    rec_template = (
        await db.execute(
            select(AccountTemplate).where(
                AccountTemplate.type == TemplateType.recette,
                AccountTemplate.name == "Recettes",
            )
        )
    ).scalar_one_or_none()

    dep_template = (
        await db.execute(
            select(AccountTemplate).where(
                AccountTemplate.type == TemplateType.depense,
                AccountTemplate.name == "Depenses",
            )
        )
    ).scalar_one_or_none()

    if not rec_template or not dep_template:
        print("ERROR: Templates not found. Run seed_templates first.")
        return

    # Build code -> template_line_id maps
    rec_lines_result = await db.execute(
        select(AccountTemplateLine).where(
            AccountTemplateLine.template_id == rec_template.id
        )
    )
    rec_code_map = {
        line.compte_code: line.id
        for line in rec_lines_result.scalars().all()
    }

    dep_lines_result = await db.execute(
        select(AccountTemplateLine).where(
            AccountTemplateLine.template_id == dep_template.id
        )
    )
    dep_code_map = {
        line.compte_code: line.id
        for line in dep_lines_result.scalars().all()
    }

    # Create CompteAdministratif
    compte = CompteAdministratif(
        collectivite_type=CollectiviteType.commune,
        collectivite_id=commune.id,
        annee_exercice=2023,
        status=CompteStatus.published,
        created_by=admin.id,
    )
    db.add(compte)
    await db.flush()
    print(f"CompteAdministratif Andrafiabe 2023 created (id={compte.id}).")

    # --- Recettes (deduplicate by code) ---
    recettes_data = parse_andrafiabe_recettes()
    seen_rec: set[str] = set()
    rec_count = 0
    for row in recettes_data:
        code = row["code"]
        tl_id = rec_code_map.get(code)
        if not tl_id or code in seen_rec:
            continue
        seen_rec.add(code)
        values = {
            k: v
            for k, v in row.items()
            if k != "code" and v != 0.0
        }
        if not values:
            values = {"budget_primitif": 0.0}
        line = RecetteLine(
            compte_admin_id=compte.id,
            template_line_id=tl_id,
            values=values,
        )
        db.add(line)
        rec_count += 1
    print(f"  Recettes: {rec_count} lines inserted.")

    # --- Depenses (3 programmes, deduplicate by code per programme) ---
    depenses_data = parse_andrafiabe_depenses()
    programme_names = list(PROGRAMME_SHEETS.values())

    for i, prog_name in enumerate(programme_names, start=1):
        prog = DepenseProgram(
            compte_admin_id=compte.id,
            numero=i,
            intitule=prog_name,
        )
        db.add(prog)
        await db.flush()

        rows = depenses_data.get(prog_name, [])
        seen_dep: set[str] = set()
        dep_count = 0
        for row in rows:
            code = row["code"]
            tl_id = dep_code_map.get(code)
            if not tl_id or code in seen_dep:
                continue
            seen_dep.add(code)
            values = {
                k: v
                for k, v in row.items()
                if k != "code" and v != 0.0
            }
            if not values:
                values = {"budget_primitif": 0.0}
            line = DepenseLine(
                programme_id=prog.id,
                template_line_id=tl_id,
                values=values,
            )
            db.add(line)
            dep_count += 1
        print(f"  Programme {i} ({prog_name}): {dep_count} lines inserted.")

    await db.commit()
    print("Compte Andrafiabe 2023 seeded successfully.")


async def main():
    async with async_session() as db:
        # 1. Admin user
        admin = await seed_admin(db)
        await db.commit()

        # 2. Templates
        print("\nSeeding templates...")
        await seed_templates(db)

        # 3. Geography
        print("\nSeeding geography...")
        commune = await seed_geography(db)
        await db.commit()

        # 4. Compte administratif Andrafiabe
        print("\nSeeding compte Andrafiabe 2023...")
        await seed_compte_andrafiabe(db, commune, admin)


if __name__ == "__main__":
    asyncio.run(main())
