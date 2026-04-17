import uuid

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.collectivity_document import CollectivityDocument
from app.models.geography import Commune, Province, Region
from app.models.user import UserRole
from tests.conftest import create_test_user, get_auth_headers


@pytest_asyncio.fixture
async def admin_headers(client: AsyncClient, db: AsyncSession) -> dict:
    await create_test_user(
        db,
        email="admin-cd@pcqvp.mg",
        password="admin12345",
        role=UserRole.admin,
    )
    return await get_auth_headers(client, "admin-cd@pcqvp.mg", "admin12345")


@pytest_asyncio.fixture
async def seed_geo(db: AsyncSession):
    province = Province(name="Antsiranana-CD", code="ANT-CD")
    db.add(province)
    await db.flush()
    region = Region(name="Diana-CD", code="DIA-CD", province_id=province.id)
    db.add(region)
    await db.flush()
    commune = Commune(name="Andrafiabe-CD", code="ANDR-CD", region_id=region.id)
    db.add(commune)
    await db.commit()
    await db.refresh(province)
    await db.refresh(region)
    await db.refresh(commune)
    return {"province": province, "region": region, "commune": commune}


async def _create_doc(
    client: AsyncClient,
    headers: dict,
    parent_type: str,
    parent_id: uuid.UUID,
    title: str = "Plan 2026",
    mime: str = "application/pdf",
    size: int = 2048,
    path: str = "/uploads/documents/abc.pdf",
):
    resp = await client.post(
        "/api/admin/collectivity-documents",
        json={
            "parent_type": parent_type,
            "parent_id": str(parent_id),
            "title": title,
            "file_path": path,
            "file_mime": mime,
            "file_size_bytes": size,
        },
        headers=headers,
    )
    return resp


@pytest.mark.asyncio
async def test_create_document_success(client: AsyncClient, admin_headers, seed_geo):
    commune = seed_geo["commune"]
    resp = await _create_doc(client, admin_headers, "commune", commune.id)
    assert resp.status_code == 201
    body = resp.json()
    assert body["parent_type"] == "commune"
    assert body["parent_id"] == str(commune.id)
    assert body["position"] == 0
    assert body["title"] == "Plan 2026"


@pytest.mark.asyncio
async def test_create_document_rejects_empty_title(
    client: AsyncClient, admin_headers, seed_geo
):
    commune = seed_geo["commune"]
    resp = await _create_doc(
        client, admin_headers, "commune", commune.id, title="   "
    )
    assert resp.status_code in (400, 422)


@pytest.mark.asyncio
async def test_create_document_rejects_unknown_mime(
    client: AsyncClient, admin_headers, seed_geo
):
    commune = seed_geo["commune"]
    resp = await _create_doc(
        client,
        admin_headers,
        "commune",
        commune.id,
        mime="application/zip",
        path="/uploads/documents/a.zip",
    )
    assert resp.status_code in (400, 422)


@pytest.mark.asyncio
async def test_list_documents_ordered_by_position(
    client: AsyncClient, admin_headers, seed_geo
):
    commune = seed_geo["commune"]
    await _create_doc(client, admin_headers, "commune", commune.id, title="Doc A")
    await _create_doc(client, admin_headers, "commune", commune.id, title="Doc B")
    await _create_doc(client, admin_headers, "commune", commune.id, title="Doc C")

    resp = await client.get(
        f"/api/admin/collectivity-documents?parent_type=commune&parent_id={commune.id}",
        headers=admin_headers,
    )
    assert resp.status_code == 200
    items = resp.json()
    assert [d["position"] for d in items] == [0, 1, 2]
    assert [d["title"] for d in items] == ["Doc A", "Doc B", "Doc C"]


@pytest.mark.asyncio
async def test_update_document_title(
    client: AsyncClient, admin_headers, seed_geo
):
    commune = seed_geo["commune"]
    created = (await _create_doc(client, admin_headers, "commune", commune.id)).json()

    resp = await client.put(
        f"/api/admin/collectivity-documents/{created['id']}",
        json={"title": "Nouveau titre"},
        headers=admin_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["title"] == "Nouveau titre"


@pytest.mark.asyncio
async def test_replace_file(client: AsyncClient, admin_headers, seed_geo):
    commune = seed_geo["commune"]
    created = (await _create_doc(client, admin_headers, "commune", commune.id)).json()

    resp = await client.put(
        f"/api/admin/collectivity-documents/{created['id']}/file",
        json={
            "file_path": "/uploads/documents/new.pdf",
            "file_mime": "application/pdf",
            "file_size_bytes": 4096,
        },
        headers=admin_headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["file_path"] == "/uploads/documents/new.pdf"
    assert body["file_size_bytes"] == 4096


@pytest.mark.asyncio
async def test_reorder_documents(client: AsyncClient, admin_headers, seed_geo):
    commune = seed_geo["commune"]
    a = (
        await _create_doc(client, admin_headers, "commune", commune.id, title="A")
    ).json()
    b = (
        await _create_doc(client, admin_headers, "commune", commune.id, title="B")
    ).json()
    c = (
        await _create_doc(client, admin_headers, "commune", commune.id, title="C")
    ).json()

    resp = await client.patch(
        "/api/admin/collectivity-documents/reorder",
        json={
            "parent_type": "commune",
            "parent_id": str(commune.id),
            "ordered_ids": [c["id"], a["id"], b["id"]],
        },
        headers=admin_headers,
    )
    assert resp.status_code == 200
    ordered = resp.json()
    assert [d["title"] for d in ordered] == ["C", "A", "B"]


@pytest.mark.asyncio
async def test_reorder_rejects_foreign_id(
    client: AsyncClient, admin_headers, seed_geo
):
    commune = seed_geo["commune"]
    a = (
        await _create_doc(client, admin_headers, "commune", commune.id, title="A")
    ).json()
    foreign = uuid.uuid4()

    resp = await client.patch(
        "/api/admin/collectivity-documents/reorder",
        json={
            "parent_type": "commune",
            "parent_id": str(commune.id),
            "ordered_ids": [a["id"], str(foreign)],
        },
        headers=admin_headers,
    )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_reorder_rejects_incomplete_list(
    client: AsyncClient, admin_headers, seed_geo
):
    commune = seed_geo["commune"]
    a = (
        await _create_doc(client, admin_headers, "commune", commune.id, title="A")
    ).json()
    await _create_doc(client, admin_headers, "commune", commune.id, title="B")

    resp = await client.patch(
        "/api/admin/collectivity-documents/reorder",
        json={
            "parent_type": "commune",
            "parent_id": str(commune.id),
            "ordered_ids": [a["id"]],
        },
        headers=admin_headers,
    )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_delete_document(
    client: AsyncClient, admin_headers, seed_geo, db: AsyncSession
):
    commune = seed_geo["commune"]
    created = (
        await _create_doc(client, admin_headers, "commune", commune.id)
    ).json()

    resp = await client.delete(
        f"/api/admin/collectivity-documents/{created['id']}",
        headers=admin_headers,
    )
    assert resp.status_code == 204

    doc_uuid = uuid.UUID(created["id"])
    result = await db.execute(
        select(CollectivityDocument).where(CollectivityDocument.id == doc_uuid)
    )
    assert result.scalar_one_or_none() is None


@pytest.mark.asyncio
async def test_check_constraint_rejects_two_parents(
    db: AsyncSession, seed_geo
):
    doc = CollectivityDocument.__new__(CollectivityDocument)
    # Use direct attribute assignment to bypass the ORM validator
    object.__setattr__(doc, "province_id", seed_geo["province"].id)
    object.__setattr__(doc, "region_id", seed_geo["region"].id)
    doc.commune_id = None
    doc.title = "Conflit"
    doc.file_path = "/uploads/documents/x.pdf"
    doc.file_mime = "application/pdf"
    doc.file_size_bytes = 100
    doc.position = 0
    db.add(doc)
    with pytest.raises(IntegrityError):
        await db.commit()
    await db.rollback()


@pytest.mark.asyncio
async def test_cascade_delete_parent_removes_documents(
    client: AsyncClient, admin_headers, seed_geo, db: AsyncSession
):
    commune = seed_geo["commune"]
    await _create_doc(client, admin_headers, "commune", commune.id, title="A")
    await _create_doc(client, admin_headers, "commune", commune.id, title="B")

    await db.delete(commune)
    await db.commit()

    result = await db.execute(
        select(CollectivityDocument).where(
            CollectivityDocument.commune_id == commune.id
        )
    )
    assert result.scalars().all() == []


@pytest.mark.asyncio
async def test_public_commune_payload_includes_documents(
    client: AsyncClient, admin_headers, seed_geo
):
    commune = seed_geo["commune"]
    await _create_doc(client, admin_headers, "commune", commune.id, title="A")
    await _create_doc(client, admin_headers, "commune", commune.id, title="B")

    resp = await client.get(f"/api/communes/{commune.id}")
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["documents"]) == 2
    assert [d["title"] for d in body["documents"]] == ["A", "B"]


@pytest.mark.asyncio
async def test_public_province_and_region_payload_includes_documents(
    client: AsyncClient, admin_headers, seed_geo
):
    province = seed_geo["province"]
    region = seed_geo["region"]
    await _create_doc(client, admin_headers, "province", province.id, title="P1")
    await _create_doc(client, admin_headers, "region", region.id, title="R1")

    p_resp = await client.get(f"/api/provinces/{province.id}")
    r_resp = await client.get(f"/api/regions/{region.id}")
    assert p_resp.status_code == 200 and r_resp.status_code == 200
    assert [d["title"] for d in p_resp.json()["documents"]] == ["P1"]
    assert [d["title"] for d in r_resp.json()["documents"]] == ["R1"]
