import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import UserRole
from tests.conftest import create_test_user, get_auth_headers


# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest_asyncio.fixture
async def admin_headers(client: AsyncClient, db: AsyncSession) -> dict:
    """Create an admin user and return auth headers."""
    await create_test_user(
        db, email="admin@geo.com", password="admin12345", role=UserRole.admin
    )
    return await get_auth_headers(client, "admin@geo.com", "admin12345")


@pytest_asyncio.fixture
async def province_payload() -> dict:
    return {"name": "Antananarivo", "code": "PRV-101", "description_json": []}


@pytest_asyncio.fixture
async def second_province_payload() -> dict:
    return {"name": "Toamasina", "code": "PRV-501", "description_json": []}


async def _create_province(client: AsyncClient, headers: dict, payload: dict) -> dict:
    """Helper: create a province via admin API and return response JSON."""
    resp = await client.post("/api/admin/provinces", json=payload, headers=headers)
    assert resp.status_code == 201
    return resp.json()


async def _create_region(
    client: AsyncClient, headers: dict, province_id: str, name: str = "Analamanga", code: str = "REG-101"
) -> dict:
    """Helper: create a region via admin API and return response JSON."""
    resp = await client.post(
        "/api/admin/regions",
        json={"name": name, "code": code, "province_id": province_id, "description_json": []},
        headers=headers,
    )
    assert resp.status_code == 201
    return resp.json()


async def _create_commune(
    client: AsyncClient, headers: dict, region_id: str, name: str = "Ambohidratrimo", code: str = "COM-101"
) -> dict:
    """Helper: create a commune via admin API and return response JSON."""
    resp = await client.post(
        "/api/admin/communes",
        json={"name": name, "code": code, "region_id": region_id, "description_json": []},
        headers=headers,
    )
    assert resp.status_code == 201
    return resp.json()


# ── 1. Public endpoints (no auth required) ───────────────────────────────────


class TestGeographyPublic:
    @pytest.mark.asyncio
    async def test_list_provinces_empty(self, client: AsyncClient):
        response = await client.get("/api/provinces")
        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_list_regions_empty(self, client: AsyncClient):
        response = await client.get("/api/regions")
        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_list_communes_empty(self, client: AsyncClient):
        response = await client.get("/api/communes")
        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_hierarchy_empty(self, client: AsyncClient):
        response = await client.get("/api/geography/hierarchy")
        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_list_provinces_returns_data(
        self, client: AsyncClient, admin_headers, province_payload
    ):
        await _create_province(client, admin_headers, province_payload)
        response = await client.get("/api/provinces")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Antananarivo"
        assert data[0]["code"] == "PRV-101"

    @pytest.mark.asyncio
    async def test_get_province_detail(
        self, client: AsyncClient, admin_headers, province_payload
    ):
        created = await _create_province(client, admin_headers, province_payload)
        response = await client.get(f"/api/provinces/{created['id']}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Antananarivo"
        assert "regions" in data

    @pytest.mark.asyncio
    async def test_get_province_not_found(self, client: AsyncClient):
        response = await client.get("/api/provinces/00000000-0000-0000-0000-000000000000")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_list_regions_returns_data(
        self, client: AsyncClient, admin_headers, province_payload
    ):
        province = await _create_province(client, admin_headers, province_payload)
        await _create_region(client, admin_headers, province["id"])
        response = await client.get("/api/regions")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Analamanga"

    @pytest.mark.asyncio
    async def test_list_regions_filter_by_province(
        self, client: AsyncClient, admin_headers, province_payload, second_province_payload
    ):
        p1 = await _create_province(client, admin_headers, province_payload)
        p2 = await _create_province(client, admin_headers, second_province_payload)
        await _create_region(client, admin_headers, p1["id"], "Analamanga", "REG-101")
        await _create_region(client, admin_headers, p2["id"], "Atsinanana", "REG-501")

        response = await client.get(f"/api/regions?province_id={p1['id']}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Analamanga"

    @pytest.mark.asyncio
    async def test_get_region_detail(
        self, client: AsyncClient, admin_headers, province_payload
    ):
        province = await _create_province(client, admin_headers, province_payload)
        region = await _create_region(client, admin_headers, province["id"])
        response = await client.get(f"/api/regions/{region['id']}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Analamanga"
        assert "communes" in data

    @pytest.mark.asyncio
    async def test_get_region_not_found(self, client: AsyncClient):
        response = await client.get("/api/regions/00000000-0000-0000-0000-000000000000")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_list_communes_returns_data(
        self, client: AsyncClient, admin_headers, province_payload
    ):
        province = await _create_province(client, admin_headers, province_payload)
        region = await _create_region(client, admin_headers, province["id"])
        await _create_commune(client, admin_headers, region["id"])
        response = await client.get("/api/communes")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Ambohidratrimo"

    @pytest.mark.asyncio
    async def test_list_communes_filter_by_region(
        self, client: AsyncClient, admin_headers, province_payload
    ):
        province = await _create_province(client, admin_headers, province_payload)
        r1 = await _create_region(client, admin_headers, province["id"], "Analamanga", "REG-101")
        r2 = await _create_region(client, admin_headers, province["id"], "Vakinankaratra", "REG-102")
        await _create_commune(client, admin_headers, r1["id"], "Ambohidratrimo", "COM-101")
        await _create_commune(client, admin_headers, r2["id"], "Antsirabe", "COM-201")

        response = await client.get(f"/api/communes?region_id={r1['id']}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Ambohidratrimo"

    @pytest.mark.asyncio
    async def test_get_commune_detail(
        self, client: AsyncClient, admin_headers, province_payload
    ):
        province = await _create_province(client, admin_headers, province_payload)
        region = await _create_region(client, admin_headers, province["id"])
        commune = await _create_commune(client, admin_headers, region["id"])
        response = await client.get(f"/api/communes/{commune['id']}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Ambohidratrimo"
        assert data["code"] == "COM-101"

    @pytest.mark.asyncio
    async def test_get_commune_not_found(self, client: AsyncClient):
        response = await client.get("/api/communes/00000000-0000-0000-0000-000000000000")
        assert response.status_code == 404


# ── 2. Auth requirement for admin endpoints ───────────────────────────────────


class TestGeographyAdminAuth:
    @pytest.mark.asyncio
    async def test_admin_list_provinces_requires_auth(self, client: AsyncClient):
        response = await client.get("/api/admin/provinces")
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_admin_create_province_requires_auth(self, client: AsyncClient):
        response = await client.post(
            "/api/admin/provinces",
            json={"name": "Test", "code": "TST", "description_json": []},
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_admin_list_regions_requires_auth(self, client: AsyncClient):
        response = await client.get("/api/admin/regions")
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_admin_create_region_requires_auth(self, client: AsyncClient):
        response = await client.post(
            "/api/admin/regions",
            json={
                "name": "Test",
                "code": "TST",
                "province_id": "00000000-0000-0000-0000-000000000000",
                "description_json": [],
            },
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_admin_list_communes_requires_auth(self, client: AsyncClient):
        response = await client.get("/api/admin/communes")
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_admin_create_commune_requires_auth(self, client: AsyncClient):
        response = await client.post(
            "/api/admin/communes",
            json={
                "name": "Test",
                "code": "TST",
                "region_id": "00000000-0000-0000-0000-000000000000",
                "description_json": [],
            },
        )
        assert response.status_code == 403


# ── 3. CRUD Province (admin) ─────────────────────────────────────────────────


class TestCrudProvince:
    @pytest.mark.asyncio
    async def test_create_province(
        self, client: AsyncClient, admin_headers, province_payload
    ):
        response = await client.post(
            "/api/admin/provinces", json=province_payload, headers=admin_headers
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Antananarivo"
        assert data["code"] == "PRV-101"
        assert "id" in data
        assert "created_at" in data

    @pytest.mark.asyncio
    async def test_create_province_with_description(
        self, client: AsyncClient, admin_headers
    ):
        payload = {
            "name": "Mahajanga",
            "code": "PRV-401",
            "description_json": [
                {"type": "heading", "content": "Titre"},
                {"type": "paragraph", "content": "Contenu descriptif."},
            ],
        }
        response = await client.post(
            "/api/admin/provinces", json=payload, headers=admin_headers
        )
        assert response.status_code == 201
        data = response.json()
        assert len(data["description_json"]) == 2
        assert data["description_json"][0]["type"] == "heading"

    @pytest.mark.asyncio
    async def test_list_provinces_admin_paginated(
        self, client: AsyncClient, admin_headers
    ):
        for i in range(5):
            await _create_province(
                client, admin_headers, {"name": f"Province {i}", "code": f"P-{i:03d}", "description_json": []}
            )

        response = await client.get(
            "/api/admin/provinces?skip=0&limit=3", headers=admin_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 5
        assert len(data["items"]) == 3

    @pytest.mark.asyncio
    async def test_update_province(
        self, client: AsyncClient, admin_headers, province_payload
    ):
        created = await _create_province(client, admin_headers, province_payload)
        update_payload = {
            "name": "Antananarivo Renivohitra",
            "code": "PRV-101",
            "description_json": [{"type": "paragraph", "content": "Updated"}],
        }
        response = await client.put(
            f"/api/admin/provinces/{created['id']}",
            json=update_payload,
            headers=admin_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Antananarivo Renivohitra"
        assert len(data["description_json"]) == 1

    @pytest.mark.asyncio
    async def test_update_province_not_found(self, client: AsyncClient, admin_headers):
        response = await client.put(
            "/api/admin/provinces/00000000-0000-0000-0000-000000000000",
            json={"name": "X", "code": "X", "description_json": []},
            headers=admin_headers,
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_province(
        self, client: AsyncClient, admin_headers, province_payload
    ):
        created = await _create_province(client, admin_headers, province_payload)
        response = await client.delete(
            f"/api/admin/provinces/{created['id']}", headers=admin_headers
        )
        assert response.status_code == 204

        # Verify it is gone
        response = await client.get(f"/api/provinces/{created['id']}")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_province_not_found(self, client: AsyncClient, admin_headers):
        response = await client.delete(
            "/api/admin/provinces/00000000-0000-0000-0000-000000000000",
            headers=admin_headers,
        )
        assert response.status_code == 404


# ── 4. CRUD Region (admin) ───────────────────────────────────────────────────


class TestCrudRegion:
    @pytest.mark.asyncio
    async def test_create_region(
        self, client: AsyncClient, admin_headers, province_payload
    ):
        province = await _create_province(client, admin_headers, province_payload)
        response = await client.post(
            "/api/admin/regions",
            json={
                "name": "Analamanga",
                "code": "REG-101",
                "province_id": province["id"],
                "description_json": [],
            },
            headers=admin_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Analamanga"
        assert data["province_id"] == province["id"]

    @pytest.mark.asyncio
    async def test_list_regions_admin_paginated(
        self, client: AsyncClient, admin_headers, province_payload
    ):
        province = await _create_province(client, admin_headers, province_payload)
        for i in range(4):
            await _create_region(
                client, admin_headers, province["id"], f"Region {i}", f"R-{i:03d}"
            )

        response = await client.get(
            f"/api/admin/regions?province_id={province['id']}&skip=0&limit=2",
            headers=admin_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 4
        assert len(data["items"]) == 2

    @pytest.mark.asyncio
    async def test_update_region(
        self, client: AsyncClient, admin_headers, province_payload
    ):
        province = await _create_province(client, admin_headers, province_payload)
        region = await _create_region(client, admin_headers, province["id"])

        update_payload = {
            "name": "Analamanga Updated",
            "code": "REG-101",
            "province_id": province["id"],
            "description_json": [],
        }
        response = await client.put(
            f"/api/admin/regions/{region['id']}",
            json=update_payload,
            headers=admin_headers,
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Analamanga Updated"

    @pytest.mark.asyncio
    async def test_update_region_not_found(self, client: AsyncClient, admin_headers):
        response = await client.put(
            "/api/admin/regions/00000000-0000-0000-0000-000000000000",
            json={
                "name": "X",
                "code": "X",
                "province_id": "00000000-0000-0000-0000-000000000000",
                "description_json": [],
            },
            headers=admin_headers,
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_region(
        self, client: AsyncClient, admin_headers, province_payload
    ):
        province = await _create_province(client, admin_headers, province_payload)
        region = await _create_region(client, admin_headers, province["id"])

        response = await client.delete(
            f"/api/admin/regions/{region['id']}", headers=admin_headers
        )
        assert response.status_code == 204

        response = await client.get(f"/api/regions/{region['id']}")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_region_not_found(self, client: AsyncClient, admin_headers):
        response = await client.delete(
            "/api/admin/regions/00000000-0000-0000-0000-000000000000",
            headers=admin_headers,
        )
        assert response.status_code == 404


# ── 5. CRUD Commune (admin) ──────────────────────────────────────────────────


class TestCrudCommune:
    @pytest.mark.asyncio
    async def test_create_commune(
        self, client: AsyncClient, admin_headers, province_payload
    ):
        province = await _create_province(client, admin_headers, province_payload)
        region = await _create_region(client, admin_headers, province["id"])

        response = await client.post(
            "/api/admin/communes",
            json={
                "name": "Ambohidratrimo",
                "code": "COM-101",
                "region_id": region["id"],
                "description_json": [],
            },
            headers=admin_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Ambohidratrimo"
        assert data["region_id"] == region["id"]

    @pytest.mark.asyncio
    async def test_list_communes_admin_paginated(
        self, client: AsyncClient, admin_headers, province_payload
    ):
        province = await _create_province(client, admin_headers, province_payload)
        region = await _create_region(client, admin_headers, province["id"])
        for i in range(4):
            await _create_commune(
                client, admin_headers, region["id"], f"Commune {i}", f"C-{i:03d}"
            )

        response = await client.get(
            f"/api/admin/communes?region_id={region['id']}&skip=1&limit=2",
            headers=admin_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 4
        assert len(data["items"]) == 2

    @pytest.mark.asyncio
    async def test_update_commune(
        self, client: AsyncClient, admin_headers, province_payload
    ):
        province = await _create_province(client, admin_headers, province_payload)
        region = await _create_region(client, admin_headers, province["id"])
        commune = await _create_commune(client, admin_headers, region["id"])

        update_payload = {
            "name": "Ambohidratrimo Updated",
            "code": "COM-101",
            "region_id": region["id"],
            "description_json": [{"type": "paragraph", "content": "Updated"}],
        }
        response = await client.put(
            f"/api/admin/communes/{commune['id']}",
            json=update_payload,
            headers=admin_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Ambohidratrimo Updated"
        assert len(data["description_json"]) == 1

    @pytest.mark.asyncio
    async def test_update_commune_not_found(self, client: AsyncClient, admin_headers):
        response = await client.put(
            "/api/admin/communes/00000000-0000-0000-0000-000000000000",
            json={
                "name": "X",
                "code": "X",
                "region_id": "00000000-0000-0000-0000-000000000000",
                "description_json": [],
            },
            headers=admin_headers,
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_commune(
        self, client: AsyncClient, admin_headers, province_payload
    ):
        province = await _create_province(client, admin_headers, province_payload)
        region = await _create_region(client, admin_headers, province["id"])
        commune = await _create_commune(client, admin_headers, region["id"])

        response = await client.delete(
            f"/api/admin/communes/{commune['id']}", headers=admin_headers
        )
        assert response.status_code == 204

        response = await client.get(f"/api/communes/{commune['id']}")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_commune_not_found(self, client: AsyncClient, admin_headers):
        response = await client.delete(
            "/api/admin/communes/00000000-0000-0000-0000-000000000000",
            headers=admin_headers,
        )
        assert response.status_code == 404


# ── 6. Referential integrity ─────────────────────────────────────────────────


class TestReferentialIntegrity:
    @pytest.mark.asyncio
    async def test_cannot_delete_province_with_regions(
        self, client: AsyncClient, admin_headers, province_payload
    ):
        province = await _create_province(client, admin_headers, province_payload)
        await _create_region(client, admin_headers, province["id"])

        response = await client.delete(
            f"/api/admin/provinces/{province['id']}", headers=admin_headers
        )
        assert response.status_code == 409
        assert "region" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_cannot_delete_region_with_communes(
        self, client: AsyncClient, admin_headers, province_payload
    ):
        province = await _create_province(client, admin_headers, province_payload)
        region = await _create_region(client, admin_headers, province["id"])
        await _create_commune(client, admin_headers, region["id"])

        response = await client.delete(
            f"/api/admin/regions/{region['id']}", headers=admin_headers
        )
        assert response.status_code == 409
        assert "commune" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_can_delete_commune_freely(
        self, client: AsyncClient, admin_headers, province_payload
    ):
        province = await _create_province(client, admin_headers, province_payload)
        region = await _create_region(client, admin_headers, province["id"])
        commune = await _create_commune(client, admin_headers, region["id"])

        response = await client.delete(
            f"/api/admin/communes/{commune['id']}", headers=admin_headers
        )
        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_can_delete_province_after_removing_children(
        self, client: AsyncClient, admin_headers, province_payload
    ):
        """Delete region first, then province should succeed."""
        province = await _create_province(client, admin_headers, province_payload)
        region = await _create_region(client, admin_headers, province["id"])

        # Delete region first
        resp = await client.delete(
            f"/api/admin/regions/{region['id']}", headers=admin_headers
        )
        assert resp.status_code == 204

        # Now province can be deleted
        resp = await client.delete(
            f"/api/admin/provinces/{province['id']}", headers=admin_headers
        )
        assert resp.status_code == 204

    @pytest.mark.asyncio
    async def test_can_delete_region_after_removing_communes(
        self, client: AsyncClient, admin_headers, province_payload
    ):
        """Delete commune first, then region should succeed."""
        province = await _create_province(client, admin_headers, province_payload)
        region = await _create_region(client, admin_headers, province["id"])
        commune = await _create_commune(client, admin_headers, region["id"])

        await client.delete(
            f"/api/admin/communes/{commune['id']}", headers=admin_headers
        )
        resp = await client.delete(
            f"/api/admin/regions/{region['id']}", headers=admin_headers
        )
        assert resp.status_code == 204


# ── 7. Unique code constraints ────────────────────────────────────────────────


class TestUniqueCodeConstraint:
    @pytest.mark.asyncio
    async def test_duplicate_province_code(
        self, client: AsyncClient, admin_headers, province_payload
    ):
        await _create_province(client, admin_headers, province_payload)
        response = await client.post(
            "/api/admin/provinces",
            json={"name": "Another Province", "code": "PRV-101", "description_json": []},
            headers=admin_headers,
        )
        assert response.status_code == 409
        assert "PRV-101" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_duplicate_region_code(
        self, client: AsyncClient, admin_headers, province_payload
    ):
        province = await _create_province(client, admin_headers, province_payload)
        await _create_region(client, admin_headers, province["id"], "Analamanga", "REG-101")
        response = await client.post(
            "/api/admin/regions",
            json={
                "name": "Another Region",
                "code": "REG-101",
                "province_id": province["id"],
                "description_json": [],
            },
            headers=admin_headers,
        )
        assert response.status_code == 409
        assert "REG-101" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_duplicate_commune_code(
        self, client: AsyncClient, admin_headers, province_payload
    ):
        province = await _create_province(client, admin_headers, province_payload)
        region = await _create_region(client, admin_headers, province["id"])
        await _create_commune(client, admin_headers, region["id"], "Ambohidratrimo", "COM-101")
        response = await client.post(
            "/api/admin/communes",
            json={
                "name": "Another Commune",
                "code": "COM-101",
                "region_id": region["id"],
                "description_json": [],
            },
            headers=admin_headers,
        )
        assert response.status_code == 409
        assert "COM-101" in response.json()["detail"]


# ── 8. Pagination and search ─────────────────────────────────────────────────


class TestPaginationAndSearch:
    @pytest.mark.asyncio
    async def test_province_search_by_name(
        self, client: AsyncClient, admin_headers
    ):
        await _create_province(
            client, admin_headers, {"name": "Antananarivo", "code": "P-001", "description_json": []}
        )
        await _create_province(
            client, admin_headers, {"name": "Toamasina", "code": "P-002", "description_json": []}
        )
        await _create_province(
            client, admin_headers, {"name": "Antsiranana", "code": "P-003", "description_json": []}
        )

        # Search for "ant" should match Antananarivo and Antsiranana (ILIKE)
        response = await client.get(
            "/api/admin/provinces?search=ant", headers=admin_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        names = [item["name"] for item in data["items"]]
        assert "Antananarivo" in names
        assert "Antsiranana" in names

    @pytest.mark.asyncio
    async def test_province_skip_and_limit(
        self, client: AsyncClient, admin_headers
    ):
        for i in range(6):
            await _create_province(
                client,
                admin_headers,
                {"name": f"Province {i:02d}", "code": f"P-{i:03d}", "description_json": []},
            )

        response = await client.get(
            "/api/admin/provinces?skip=2&limit=2", headers=admin_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 6
        assert len(data["items"]) == 2

    @pytest.mark.asyncio
    async def test_region_search_by_name(
        self, client: AsyncClient, admin_headers, province_payload
    ):
        province = await _create_province(client, admin_headers, province_payload)
        await _create_region(client, admin_headers, province["id"], "Analamanga", "R-001")
        await _create_region(client, admin_headers, province["id"], "Vakinankaratra", "R-002")
        await _create_region(client, admin_headers, province["id"], "Analanjirofo", "R-003")

        response = await client.get(
            "/api/admin/regions?search=anala", headers=admin_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2

    @pytest.mark.asyncio
    async def test_commune_search_by_name(
        self, client: AsyncClient, admin_headers, province_payload
    ):
        province = await _create_province(client, admin_headers, province_payload)
        region = await _create_region(client, admin_headers, province["id"])
        await _create_commune(client, admin_headers, region["id"], "Ambohidratrimo", "C-001")
        await _create_commune(client, admin_headers, region["id"], "Ambohimanga", "C-002")
        await _create_commune(client, admin_headers, region["id"], "Tanjombato", "C-003")

        response = await client.get(
            "/api/admin/communes?search=ambohi", headers=admin_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        names = [item["name"] for item in data["items"]]
        assert "Ambohidratrimo" in names
        assert "Ambohimanga" in names


# ── 9. Hierarchy endpoint ────────────────────────────────────────────────────


class TestHierarchy:
    @pytest.mark.asyncio
    async def test_hierarchy_full_tree(
        self, client: AsyncClient, admin_headers, province_payload
    ):
        province = await _create_province(client, admin_headers, province_payload)
        region = await _create_region(client, admin_headers, province["id"])
        await _create_commune(client, admin_headers, region["id"])

        response = await client.get("/api/geography/hierarchy")
        assert response.status_code == 200
        data = response.json()

        assert len(data) == 1
        prov = data[0]
        assert prov["name"] == "Antananarivo"
        assert prov["code"] == "PRV-101"
        assert len(prov["regions"]) == 1

        reg = prov["regions"][0]
        assert reg["name"] == "Analamanga"
        assert reg["code"] == "REG-101"
        assert len(reg["communes"]) == 1

        comm = reg["communes"][0]
        assert comm["name"] == "Ambohidratrimo"
        assert comm["code"] == "COM-101"

    @pytest.mark.asyncio
    async def test_hierarchy_multiple_provinces(
        self, client: AsyncClient, admin_headers, province_payload, second_province_payload
    ):
        p1 = await _create_province(client, admin_headers, province_payload)
        p2 = await _create_province(client, admin_headers, second_province_payload)
        await _create_region(client, admin_headers, p1["id"], "Analamanga", "REG-101")
        await _create_region(client, admin_headers, p2["id"], "Atsinanana", "REG-501")

        response = await client.get("/api/geography/hierarchy")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        names = [p["name"] for p in data]
        assert "Antananarivo" in names
        assert "Toamasina" in names

    @pytest.mark.asyncio
    async def test_hierarchy_no_auth_required(self, client: AsyncClient):
        """The hierarchy endpoint is public and should not require auth."""
        response = await client.get("/api/geography/hierarchy")
        assert response.status_code == 200
