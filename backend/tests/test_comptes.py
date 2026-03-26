import uuid

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account_template import (
    AccountTemplate,
    AccountTemplateColumn,
    AccountTemplateLine,
    ColumnDataType,
    SectionType,
    TemplateType,
)
from app.models.geography import Commune, Province, Region
from app.models.user import UserRole
from tests.conftest import create_test_user, get_auth_headers

# --- Fixtures ---


@pytest_asyncio.fixture
async def admin_user(db: AsyncSession):
    return await create_test_user(
        db, email="admin@pcqvp.mg", password="admin123", role=UserRole.admin
    )


@pytest_asyncio.fixture
async def editor_user(db: AsyncSession):
    return await create_test_user(
        db, email="editor@pcqvp.mg", password="editor123", role=UserRole.editor
    )


@pytest_asyncio.fixture
async def admin_headers(client: AsyncClient, admin_user):
    return await get_auth_headers(client, "admin@pcqvp.mg", "admin123")


@pytest_asyncio.fixture
async def editor_headers(client: AsyncClient, editor_user):
    return await get_auth_headers(client, "editor@pcqvp.mg", "editor123")


@pytest_asyncio.fixture
async def seed_geography(db: AsyncSession):
    """Create province → region → commune hierarchy."""
    province = Province(name="Antsiranana", code="ANT")
    db.add(province)
    await db.flush()

    region = Region(
        name="Diana", code="DIA", province_id=province.id
    )
    db.add(region)
    await db.flush()

    commune = Commune(
        name="Andrafiabe", code="ANDR", region_id=region.id
    )
    db.add(commune)
    await db.commit()
    await db.refresh(province)
    await db.refresh(region)
    await db.refresh(commune)
    return {"province": province, "region": region, "commune": commune}


@pytest_asyncio.fixture
async def seed_templates(db: AsyncSession):
    """Create recette and depense templates with lines and columns."""
    # Recette template
    rec_template = AccountTemplate(
        name="Recettes communes", type=TemplateType.recette, version=1, is_active=True
    )
    db.add(rec_template)
    await db.flush()

    # Niv1
    rec_niv1 = AccountTemplateLine(
        template_id=rec_template.id,
        compte_code="70",
        intitule="Recettes fiscales",
        level=1,
        parent_code=None,
        section=SectionType.fonctionnement,
        sort_order=1,
    )
    db.add(rec_niv1)
    # Niv2
    rec_niv2 = AccountTemplateLine(
        template_id=rec_template.id,
        compte_code="708",
        intitule="Impots sur les revenus",
        level=2,
        parent_code="70",
        section=SectionType.fonctionnement,
        sort_order=2,
    )
    db.add(rec_niv2)
    # Niv3
    rec_niv3 = AccountTemplateLine(
        template_id=rec_template.id,
        compte_code="7080",
        intitule="Impots sur les revenus des personnes",
        level=3,
        parent_code="708",
        section=SectionType.fonctionnement,
        sort_order=3,
    )
    db.add(rec_niv3)

    # Columns for recette
    for i, (code, name, computed) in enumerate([
        ("budget_primitif", "Budget primitif", False),
        ("budget_additionnel", "Budget additionnel", False),
        ("modifications", "Modifications", False),
        ("previsions_definitives", "Previsions definitives", True),
        ("or_admis", "OR admis", False),
        ("recouvrement", "Recouvrement", False),
    ]):
        db.add(AccountTemplateColumn(
            template_id=rec_template.id,
            name=name,
            code=code,
            data_type=ColumnDataType.number,
            is_computed=computed,
            sort_order=i + 1,
        ))

    # Depense template
    dep_template = AccountTemplate(
        name="Depenses communes", type=TemplateType.depense, version=1, is_active=True
    )
    db.add(dep_template)
    await db.flush()

    dep_niv1 = AccountTemplateLine(
        template_id=dep_template.id,
        compte_code="60",
        intitule="Charges du personnel",
        level=1,
        parent_code=None,
        section=SectionType.fonctionnement,
        sort_order=1,
    )
    db.add(dep_niv1)
    dep_niv2 = AccountTemplateLine(
        template_id=dep_template.id,
        compte_code="601",
        intitule="Salaires",
        level=2,
        parent_code="60",
        section=SectionType.fonctionnement,
        sort_order=2,
    )
    db.add(dep_niv2)
    dep_niv3 = AccountTemplateLine(
        template_id=dep_template.id,
        compte_code="6010",
        intitule="Salaires de base",
        level=3,
        parent_code="601",
        section=SectionType.fonctionnement,
        sort_order=3,
    )
    db.add(dep_niv3)

    for i, (code, name, computed) in enumerate([
        ("budget_primitif", "Budget primitif", False),
        ("budget_additionnel", "Budget additionnel", False),
        ("modifications", "Modifications", False),
        ("previsions_definitives", "Previsions definitives", True),
        ("engagement", "Engagement", False),
        ("mandat_admis", "Mandat admis", False),
        ("paiement", "Paiement", False),
    ]):
        db.add(AccountTemplateColumn(
            template_id=dep_template.id,
            name=name,
            code=code,
            data_type=ColumnDataType.number,
            is_computed=computed,
            sort_order=i + 1,
        ))

    await db.commit()
    await db.refresh(rec_template)
    await db.refresh(dep_template)
    return {"recette": rec_template, "depense": dep_template}


# --- Tests CRUD Compte ---


@pytest.mark.asyncio
async def test_create_compte(
    client: AsyncClient, admin_headers, seed_geography, seed_templates
):
    commune = seed_geography["commune"]
    response = await client.post(
        "/api/admin/comptes",
        json={
            "collectivite_type": "commune",
            "collectivite_id": str(commune.id),
            "annee_exercice": 2023,
        },
        headers=admin_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["collectivite_name"] == "Andrafiabe"
    assert data["annee_exercice"] == 2023
    assert data["status"] == "draft"
    assert len(data["programmes"]) == 3
    assert data["programmes"][0]["intitule"] == "Administration et Coordination"


@pytest.mark.asyncio
async def test_create_compte_duplicate(
    client: AsyncClient, admin_headers, seed_geography, seed_templates
):
    commune = seed_geography["commune"]
    body = {
        "collectivite_type": "commune",
        "collectivite_id": str(commune.id),
        "annee_exercice": 2023,
    }
    r1 = await client.post("/api/admin/comptes", json=body, headers=admin_headers)
    assert r1.status_code == 201

    r2 = await client.post("/api/admin/comptes", json=body, headers=admin_headers)
    assert r2.status_code == 409


@pytest.mark.asyncio
async def test_create_compte_invalid_collectivite(
    client: AsyncClient, admin_headers, seed_templates
):
    response = await client.post(
        "/api/admin/comptes",
        json={
            "collectivite_type": "commune",
            "collectivite_id": str(uuid.uuid4()),
            "annee_exercice": 2023,
        },
        headers=admin_headers,
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_compte(
    client: AsyncClient, admin_headers, seed_geography, seed_templates
):
    commune = seed_geography["commune"]
    r1 = await client.post(
        "/api/admin/comptes",
        json={
            "collectivite_type": "commune",
            "collectivite_id": str(commune.id),
            "annee_exercice": 2023,
        },
        headers=admin_headers,
    )
    compte_id = r1.json()["id"]

    r2 = await client.get(f"/api/admin/comptes/{compte_id}", headers=admin_headers)
    assert r2.status_code == 200
    data = r2.json()
    assert data["collectivite_name"] == "Andrafiabe"
    assert "recettes" in data


# --- Tests Recette Upsert ---


@pytest.mark.asyncio
async def test_upsert_recette(
    client: AsyncClient, admin_headers, seed_geography, seed_templates
):
    commune = seed_geography["commune"]
    r1 = await client.post(
        "/api/admin/comptes",
        json={
            "collectivite_type": "commune",
            "collectivite_id": str(commune.id),
            "annee_exercice": 2023,
        },
        headers=admin_headers,
    )
    compte_id = r1.json()["id"]

    # Get template line id
    rec_template = seed_templates["recette"]
    niv3_line = [ln for ln in rec_template.lines if ln.level == 3][0]

    # Upsert
    r2 = await client.put(
        f"/api/admin/comptes/{compte_id}/recettes",
        json={
            "template_line_id": str(niv3_line.id),
            "values": {
                "budget_primitif": 1017922,
                "budget_additionnel": 0,
                "modifications": 0,
                "or_admis": 1017922,
                "recouvrement": 0,
            },
        },
        headers=admin_headers,
    )
    assert r2.status_code == 200
    data = r2.json()
    assert data["computed"]["previsions_definitives"] == 1017922
    assert data["computed"]["reste_a_recouvrer"] == 1017922


# --- Tests Programme CRUD ---


@pytest.mark.asyncio
async def test_add_programme(
    client: AsyncClient, admin_headers, seed_geography, seed_templates
):
    commune = seed_geography["commune"]
    r1 = await client.post(
        "/api/admin/comptes",
        json={
            "collectivite_type": "commune",
            "collectivite_id": str(commune.id),
            "annee_exercice": 2023,
        },
        headers=admin_headers,
    )
    compte_id = r1.json()["id"]

    r2 = await client.post(
        f"/api/admin/comptes/{compte_id}/programmes",
        json={"intitule": "Programme IV"},
        headers=admin_headers,
    )
    assert r2.status_code == 201
    assert r2.json()["numero"] == 4


@pytest.mark.asyncio
async def test_delete_programme(
    client: AsyncClient, admin_headers, seed_geography, seed_templates
):
    commune = seed_geography["commune"]
    r1 = await client.post(
        "/api/admin/comptes",
        json={
            "collectivite_type": "commune",
            "collectivite_id": str(commune.id),
            "annee_exercice": 2023,
        },
        headers=admin_headers,
    )
    compte_id = r1.json()["id"]
    prog_id = r1.json()["programmes"][2]["id"]

    r2 = await client.delete(
        f"/api/admin/comptes/{compte_id}/programmes/{prog_id}",
        headers=admin_headers,
    )
    assert r2.status_code == 204


# --- Tests Status ---


@pytest.mark.asyncio
async def test_publish_admin_only(
    client: AsyncClient,
    admin_headers,
    editor_headers,
    seed_geography,
    seed_templates,
):
    commune = seed_geography["commune"]
    r1 = await client.post(
        "/api/admin/comptes",
        json={
            "collectivite_type": "commune",
            "collectivite_id": str(commune.id),
            "annee_exercice": 2023,
        },
        headers=admin_headers,
    )
    compte_id = r1.json()["id"]

    # Editor cannot publish
    r2 = await client.put(
        f"/api/admin/comptes/{compte_id}/status",
        json={"status": "published"},
        headers=editor_headers,
    )
    assert r2.status_code == 403

    # Admin can publish
    r3 = await client.put(
        f"/api/admin/comptes/{compte_id}/status",
        json={"status": "published"},
        headers=admin_headers,
    )
    assert r3.status_code == 200
    assert r3.json()["status"] == "published"


# --- Tests Changelog ---


@pytest.mark.asyncio
async def test_changelog_on_published(
    client: AsyncClient, admin_headers, seed_geography, seed_templates
):
    commune = seed_geography["commune"]
    r1 = await client.post(
        "/api/admin/comptes",
        json={
            "collectivite_type": "commune",
            "collectivite_id": str(commune.id),
            "annee_exercice": 2023,
        },
        headers=admin_headers,
    )
    compte_id = r1.json()["id"]

    # Publish
    await client.put(
        f"/api/admin/comptes/{compte_id}/status",
        json={"status": "published"},
        headers=admin_headers,
    )

    # Modify recette (should create changelog)
    rec_template = seed_templates["recette"]
    niv3_line = [ln for ln in rec_template.lines if ln.level == 3][0]
    await client.put(
        f"/api/admin/comptes/{compte_id}/recettes",
        json={
            "template_line_id": str(niv3_line.id),
            "values": {"budget_primitif": 500000},
        },
        headers=admin_headers,
    )

    # Check changelog
    r4 = await client.get(
        f"/api/admin/comptes/{compte_id}/changelog",
        headers=admin_headers,
    )
    assert r4.status_code == 200
    data = r4.json()
    # At least status_change + recette_update
    assert data["total"] >= 2


# --- Tests List ---


@pytest.mark.asyncio
async def test_list_comptes(
    client: AsyncClient, admin_headers, seed_geography, seed_templates
):
    commune = seed_geography["commune"]
    await client.post(
        "/api/admin/comptes",
        json={
            "collectivite_type": "commune",
            "collectivite_id": str(commune.id),
            "annee_exercice": 2023,
        },
        headers=admin_headers,
    )

    r = await client.get("/api/admin/comptes", headers=admin_headers)
    assert r.status_code == 200
    assert r.json()["total"] >= 1


@pytest.mark.asyncio
async def test_list_comptes_filter(
    client: AsyncClient, admin_headers, seed_geography, seed_templates
):
    commune = seed_geography["commune"]
    await client.post(
        "/api/admin/comptes",
        json={
            "collectivite_type": "commune",
            "collectivite_id": str(commune.id),
            "annee_exercice": 2023,
        },
        headers=admin_headers,
    )

    r = await client.get(
        "/api/admin/comptes?annee=2023", headers=admin_headers
    )
    assert r.status_code == 200
    assert r.json()["total"] >= 1

    r2 = await client.get(
        "/api/admin/comptes?annee=1999", headers=admin_headers
    )
    assert r2.json()["total"] == 0


# --- Tests Recapitulatifs ---


@pytest.mark.asyncio
async def test_recap_recettes(
    client: AsyncClient, admin_headers, seed_geography, seed_templates
):
    commune = seed_geography["commune"]
    r1 = await client.post(
        "/api/admin/comptes",
        json={
            "collectivite_type": "commune",
            "collectivite_id": str(commune.id),
            "annee_exercice": 2023,
        },
        headers=admin_headers,
    )
    compte_id = r1.json()["id"]

    r = await client.get(
        f"/api/admin/comptes/{compte_id}/recapitulatifs/recettes",
        headers=admin_headers,
    )
    assert r.status_code == 200
    assert "sections" in r.json()


@pytest.mark.asyncio
async def test_equilibre(
    client: AsyncClient, admin_headers, seed_geography, seed_templates
):
    commune = seed_geography["commune"]
    r1 = await client.post(
        "/api/admin/comptes",
        json={
            "collectivite_type": "commune",
            "collectivite_id": str(commune.id),
            "annee_exercice": 2023,
        },
        headers=admin_headers,
    )
    compte_id = r1.json()["id"]

    r = await client.get(
        f"/api/admin/comptes/{compte_id}/recapitulatifs/equilibre",
        headers=admin_headers,
    )
    assert r.status_code == 200
    data = r.json()
    assert "fonctionnement" in data
    assert "investissement" in data
    assert "resultat_definitif" in data
