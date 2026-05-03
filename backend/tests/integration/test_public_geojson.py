"""Tests d'intégration de l'endpoint public /api/geography/regions/geojson."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_no_active_version_returns_503(client: AsyncClient):
    r = await client.get("/api/geography/regions/geojson")
    assert r.status_code == 503
