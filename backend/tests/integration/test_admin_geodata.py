"""Tests d'intégration des endpoints admin geodata + endpoint public."""

import io
import json
import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import UserRole
from tests.conftest import create_test_user, get_auth_headers


def _square(lat: float, lon: float, name: str, level: str = "4", d: float = 0.4) -> dict:
    coords = [
        [lon - d, lat - d],
        [lon + d, lat - d],
        [lon + d, lat + d],
        [lon - d, lat + d],
        [lon - d, lat - d],
    ]
    return {
        "type": "Feature",
        "properties": {"name": name, "admin_level": level},
        "geometry": {"type": "Polygon", "coordinates": [coords]},
    }


def _geojson_n(n: int) -> bytes:
    feats = [_square(-18 + i * 0.5, 47 + i * 0.1, f"Region{i}") for i in range(n)]
    return json.dumps({"type": "FeatureCollection", "features": feats}).encode()


async def _admin_headers(client: AsyncClient, db: AsyncSession) -> dict:
    await create_test_user(
        db, email="admin@test.local", password="password123", role=UserRole.admin
    )
    return await get_auth_headers(
        client, email="admin@test.local", password="password123"
    )


async def _editor_headers(client: AsyncClient, db: AsyncSession) -> dict:
    await create_test_user(
        db,
        email="editor@test.local",
        password="password123",
        role=UserRole.editor,
    )
    return await get_auth_headers(
        client, email="editor@test.local", password="password123"
    )


@pytest.mark.asyncio
async def test_upload_then_activate_then_public_serves(
    client: AsyncClient, db: AsyncSession
):
    headers = await _admin_headers(client, db)
    files = {"file": ("regions.geojson", io.BytesIO(_geojson_n(23)), "application/geo+json")}
    r = await client.post(
        "/api/admin/geodata/regions/upload", headers=headers, files=files
    )
    assert r.status_code == 201, r.text
    body = r.json()
    version_id = body["version_id"]

    r2 = await client.post(
        f"/api/admin/geodata/regions/versions/{version_id}/activate",
        headers=headers,
    )
    assert r2.status_code == 200, r2.text

    r3 = await client.get("/api/geography/regions/geojson")
    assert r3.status_code == 200
    assert "ETag" in r3.headers
    payload = r3.json()
    assert payload["type"] == "FeatureCollection"


@pytest.mark.asyncio
async def test_public_endpoint_etag_then_304(
    client: AsyncClient, db: AsyncSession
):
    headers = await _admin_headers(client, db)
    files = {"file": ("regions.geojson", io.BytesIO(_geojson_n(23)), "application/geo+json")}
    r = await client.post(
        "/api/admin/geodata/regions/upload", headers=headers, files=files
    )
    vid = r.json()["version_id"]
    await client.post(
        f"/api/admin/geodata/regions/versions/{vid}/activate", headers=headers
    )
    r1 = await client.get("/api/geography/regions/geojson")
    etag = r1.headers["ETag"]
    r2 = await client.get(
        "/api/geography/regions/geojson", headers={"If-None-Match": etag}
    )
    assert r2.status_code == 304


@pytest.mark.asyncio
async def test_editor_role_cannot_access_admin_geodata(
    client: AsyncClient, db: AsyncSession
):
    headers = await _editor_headers(client, db)
    files = {"file": ("regions.geojson", io.BytesIO(_geojson_n(23)), "application/geo+json")}
    r = await client.post(
        "/api/admin/geodata/regions/upload", headers=headers, files=files
    )
    assert r.status_code == 403


@pytest.mark.asyncio
async def test_reject_csv_extension_returns_400(
    client: AsyncClient, db: AsyncSession
):
    headers = await _admin_headers(client, db)
    files = {"file": ("data.csv", io.BytesIO(b"a,b\n1,2"), "text/csv")}
    r = await client.post(
        "/api/admin/geodata/regions/upload", headers=headers, files=files
    )
    assert r.status_code == 400


@pytest.mark.asyncio
async def test_list_versions_paginated(
    client: AsyncClient, db: AsyncSession
):
    headers = await _admin_headers(client, db)
    for _ in range(3):
        files = {"file": ("regions.geojson", io.BytesIO(_geojson_n(23)), "application/geo+json")}
        await client.post(
            "/api/admin/geodata/regions/upload", headers=headers, files=files
        )
    r = await client.get(
        "/api/admin/geodata/regions/versions?limit=2&offset=0", headers=headers
    )
    assert r.status_code == 200
    body = r.json()
    assert body["total"] >= 3
    assert len(body["items"]) == 2


@pytest.mark.asyncio
async def test_delete_active_returns_409(
    client: AsyncClient, db: AsyncSession
):
    headers = await _admin_headers(client, db)
    files = {"file": ("regions.geojson", io.BytesIO(_geojson_n(23)), "application/geo+json")}
    r = await client.post(
        "/api/admin/geodata/regions/upload", headers=headers, files=files
    )
    vid = r.json()["version_id"]
    await client.post(
        f"/api/admin/geodata/regions/versions/{vid}/activate", headers=headers
    )
    r2 = await client.delete(
        f"/api/admin/geodata/regions/versions/{vid}", headers=headers
    )
    assert r2.status_code == 409


@pytest.mark.asyncio
async def test_delete_inactive_succeeds_204(
    client: AsyncClient, db: AsyncSession
):
    headers = await _admin_headers(client, db)
    files = {"file": ("regions.geojson", io.BytesIO(_geojson_n(23)), "application/geo+json")}
    r = await client.post(
        "/api/admin/geodata/regions/upload", headers=headers, files=files
    )
    vid = r.json()["version_id"]
    r2 = await client.delete(
        f"/api/admin/geodata/regions/versions/{vid}", headers=headers
    )
    assert r2.status_code == 204


@pytest.mark.asyncio
async def test_reject_xml_content_returns_400(
    client: AsyncClient, db: AsyncSession
):
    headers = await _admin_headers(client, db)
    files = {
        "file": (
            "data.geojson",
            io.BytesIO(b"<?xml version='1.0'?><root/>"),
            "application/json",
        )
    }
    r = await client.post(
        "/api/admin/geodata/regions/upload", headers=headers, files=files
    )
    assert r.status_code == 400


@pytest.mark.asyncio
async def test_reject_geojson_without_admin_level_4(
    client: AsyncClient, db: AsyncSession
):
    headers = await _admin_headers(client, db)
    feats = [_square(-18, 47, "City", level="6")]
    payload = json.dumps({"type": "FeatureCollection", "features": feats}).encode()
    files = {"file": ("regions.geojson", io.BytesIO(payload), "application/geo+json")}
    r = await client.post(
        "/api/admin/geodata/regions/upload", headers=headers, files=files
    )
    assert r.status_code == 400
    body = r.json()
    detail = body.get("detail")
    if isinstance(detail, dict):
        assert detail.get("code") == "NO_FEATURES"


@pytest.mark.asyncio
async def test_reject_file_over_50mb_returns_413(
    client: AsyncClient, db: AsyncSession
):
    """Simule un dépassement de quota en patchant la limite via un override."""
    from app.routers import admin_geodata as mod

    original = mod.settings.GEODATA_MAX_UPLOAD_BYTES
    mod.settings.GEODATA_MAX_UPLOAD_BYTES = 1024  # 1 Ko pour le test
    try:
        headers = await _admin_headers(client, db)
        big = b"x" * 4096
        files = {"file": ("regions.geojson", io.BytesIO(big), "application/geo+json")}
        r = await client.post(
            "/api/admin/geodata/regions/upload", headers=headers, files=files
        )
        assert r.status_code == 413
    finally:
        mod.settings.GEODATA_MAX_UPLOAD_BYTES = original


@pytest.mark.asyncio
async def test_strips_html_js_properties(
    client: AsyncClient, db: AsyncSession
):
    headers = await _admin_headers(client, db)
    feats = []
    for i in range(23):
        f = _square(-18 + i * 0.5, 47 + i * 0.1, f"Region{i}")
        f["properties"]["evil"] = "<script>alert(1)</script>"
        f["properties"]["other"] = "<b>html</b>"
        feats.append(f)
    payload = json.dumps({"type": "FeatureCollection", "features": feats}).encode()
    files = {"file": ("regions.geojson", io.BytesIO(payload), "application/geo+json")}
    r = await client.post(
        "/api/admin/geodata/regions/upload", headers=headers, files=files
    )
    assert r.status_code == 201
    vid = r.json()["version_id"]
    r2 = await client.get(
        f"/api/admin/geodata/regions/versions/{vid}", headers=headers
    )
    detail = r2.json()
    for feat in detail["geojson_processed"]["features"]:
        keys = set(feat.get("properties", {}).keys())
        assert keys <= {"name", "name_official", "region_code", "admin_level"}


@pytest.mark.asyncio
async def test_pipeline_emits_region_not_in_database_warning(
    client: AsyncClient, db: AsyncSession
):
    """Les noms inconnus de la table regions génèrent un warning."""
    headers = await _admin_headers(client, db)
    files = {"file": ("regions.geojson", io.BytesIO(_geojson_n(23)), "application/geo+json")}
    r = await client.post(
        "/api/admin/geodata/regions/upload", headers=headers, files=files
    )
    assert r.status_code == 201
    body = r.json()
    codes = {w["code"] for w in body["warnings"]}
    # Aucune table regions seedée en test : tous inconnus
    assert "REGION_NOT_IN_DATABASE" in codes


@pytest.mark.asyncio
async def test_pipeline_emits_feature_count_out_of_range(
    client: AsyncClient, db: AsyncSession
):
    headers = await _admin_headers(client, db)
    # 5 régions seulement → hors plage 20-30
    files = {"file": ("regions.geojson", io.BytesIO(_geojson_n(5)), "application/geo+json")}
    r = await client.post(
        "/api/admin/geodata/regions/upload", headers=headers, files=files
    )
    assert r.status_code == 201
    codes = {w["code"] for w in r.json()["warnings"]}
    assert "FEATURE_COUNT_OUT_OF_RANGE" in codes


@pytest.mark.asyncio
async def test_rollback_restores_previous_geojson(
    client: AsyncClient, db: AsyncSession
):
    headers = await _admin_headers(client, db)
    files1 = {"file": ("v1.geojson", io.BytesIO(_geojson_n(23)), "application/geo+json")}
    r1 = await client.post(
        "/api/admin/geodata/regions/upload", headers=headers, files=files1
    )
    v1 = r1.json()["version_id"]
    files2 = {"file": ("v2.geojson", io.BytesIO(_geojson_n(24)), "application/geo+json")}
    r2 = await client.post(
        "/api/admin/geodata/regions/upload", headers=headers, files=files2
    )
    v2 = r2.json()["version_id"]
    await client.post(
        f"/api/admin/geodata/regions/versions/{v1}/activate", headers=headers
    )
    await client.post(
        f"/api/admin/geodata/regions/versions/{v2}/activate", headers=headers
    )
    rA = await client.get("/api/geography/regions/geojson")
    etag2 = rA.headers["ETag"]
    await client.post(
        f"/api/admin/geodata/regions/versions/{v1}/activate", headers=headers
    )
    rB = await client.get("/api/geography/regions/geojson")
    etag1 = rB.headers["ETag"]
    assert etag1 != etag2
    assert len(rB.json()["features"]) == 23

