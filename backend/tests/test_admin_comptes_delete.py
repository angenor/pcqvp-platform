import uuid

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog
from app.models.compte_administratif import (
    CollectiviteType,
    CompteAdministratif,
    CompteStatus,
)
from app.models.geography import Commune, Province, Region
from app.models.user import UserRole
from tests.conftest import create_test_user, get_auth_headers


@pytest_asyncio.fixture
async def admin_user(db: AsyncSession):
    return await create_test_user(
        db,
        email="admin-delete@pcqvp.mg",
        password="admin12345",
        role=UserRole.admin,
    )


@pytest_asyncio.fixture
async def admin_headers(client: AsyncClient, admin_user):
    return await get_auth_headers(client, "admin-delete@pcqvp.mg", "admin12345")


@pytest_asyncio.fixture
async def editor_headers(client: AsyncClient, db: AsyncSession):
    await create_test_user(
        db,
        email="editor-delete@pcqvp.mg",
        password="editor12345",
        role=UserRole.editor,
    )
    return await get_auth_headers(client, "editor-delete@pcqvp.mg", "editor12345")


@pytest_asyncio.fixture
async def seed_commune(db: AsyncSession):
    province = Province(name="Antsiranana", code="ANT-DEL")
    db.add(province)
    await db.flush()
    region = Region(name="Diana", code="DIA-DEL", province_id=province.id)
    db.add(region)
    await db.flush()
    commune = Commune(name="Andrafiabe", code="ANDR-DEL", region_id=region.id)
    db.add(commune)
    await db.commit()
    await db.refresh(commune)
    return commune


@pytest_asyncio.fixture
async def draft_compte(
    db: AsyncSession, admin_user, seed_commune
) -> CompteAdministratif:
    compte = CompteAdministratif(
        collectivite_type=CollectiviteType.commune,
        collectivite_id=seed_commune.id,
        annee_exercice=2024,
        status=CompteStatus.draft,
        created_by=admin_user.id,
    )
    db.add(compte)
    await db.commit()
    await db.refresh(compte)
    return compte


@pytest_asyncio.fixture
async def published_compte(
    db: AsyncSession, admin_user, seed_commune
) -> CompteAdministratif:
    compte = CompteAdministratif(
        collectivite_type=CollectiviteType.commune,
        collectivite_id=seed_commune.id,
        annee_exercice=2023,
        status=CompteStatus.published,
        created_by=admin_user.id,
    )
    db.add(compte)
    await db.commit()
    await db.refresh(compte)
    return compte


@pytest.mark.asyncio
async def test_delete_draft_compte_returns_204(
    client: AsyncClient, admin_headers, draft_compte, db: AsyncSession
):
    resp = await client.delete(
        f"/api/admin/comptes/{draft_compte.id}", headers=admin_headers
    )
    assert resp.status_code == 204

    result = await db.execute(
        select(CompteAdministratif).where(CompteAdministratif.id == draft_compte.id)
    )
    assert result.scalar_one_or_none() is None


@pytest.mark.asyncio
async def test_delete_published_compte_returns_409(
    client: AsyncClient, admin_headers, published_compte, db: AsyncSession
):
    resp = await client.delete(
        f"/api/admin/comptes/{published_compte.id}", headers=admin_headers
    )
    assert resp.status_code == 409
    body = resp.json()
    detail = body.get("detail", body)
    assert detail["error"] == "compte_published"
    assert detail["required_action"] == "set_status_draft"
    assert "brouillon" in detail["message"].lower()

    result = await db.execute(
        select(CompteAdministratif).where(
            CompteAdministratif.id == published_compte.id
        )
    )
    assert result.scalar_one_or_none() is not None


@pytest.mark.asyncio
async def test_delete_compte_forbidden_for_editor(
    client: AsyncClient, editor_headers, draft_compte
):
    resp = await client.delete(
        f"/api/admin/comptes/{draft_compte.id}", headers=editor_headers
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_delete_compte_audit_log_entry(
    client: AsyncClient, admin_headers, admin_user, draft_compte, db: AsyncSession
):
    compte_id = draft_compte.id
    annee = draft_compte.annee_exercice
    resp = await client.delete(
        f"/api/admin/comptes/{compte_id}", headers=admin_headers
    )
    assert resp.status_code == 204

    result = await db.execute(
        select(AuditLog).where(
            AuditLog.action == "compte_administratif.deleted",
            AuditLog.target_id == compte_id,
        )
    )
    entry = result.scalar_one()
    assert entry.actor_user_id == admin_user.id
    assert entry.target_type == "compte_administratif"
    assert entry.payload["id"] == str(compte_id)
    assert entry.payload["annee_exercice"] == annee
    assert entry.payload["status"] == "draft"


@pytest.mark.asyncio
async def test_delete_compte_not_found(client: AsyncClient, admin_headers):
    resp = await client.delete(
        f"/api/admin/comptes/{uuid.uuid4()}", headers=admin_headers
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_compte_requires_auth(client: AsyncClient, draft_compte):
    resp = await client.delete(f"/api/admin/comptes/{draft_compte.id}")
    assert resp.status_code in (401, 403)
