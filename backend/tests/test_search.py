import uuid

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.geography import Commune, Province, Region


@pytest_asyncio.fixture
async def seed_geography(db: AsyncSession):
    """Seed provinces, regions, communes for search tests."""
    province = Province(
        id=uuid.uuid4(),
        name="Antananarivo",
        code="P01",
    )
    db.add(province)
    await db.flush()

    region = Region(
        id=uuid.uuid4(),
        name="Analamanga",
        code="R01",
        province_id=province.id,
    )
    db.add(region)
    await db.flush()

    commune1 = Commune(
        id=uuid.uuid4(),
        name="Antananarivo Renivohitra",
        code="C01",
        region_id=region.id,
    )
    commune2 = Commune(
        id=uuid.uuid4(),
        name="Ambohidratrimo",
        code="C02",
        region_id=region.id,
    )
    db.add_all([commune1, commune2])
    await db.commit()

    return {"province": province, "region": region, "communes": [commune1, commune2]}


@pytest.mark.asyncio
async def test_search_by_name(client: AsyncClient, seed_geography):
    response = await client.get("/api/search?q=Antananarivo")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] > 0
    names = [
        r["name"]
        for r in data["results"]["collectivites"]
    ]
    assert any("Antananarivo" in n for n in names)


@pytest.mark.asyncio
async def test_search_no_results(client: AsyncClient, seed_geography):
    response = await client.get("/api/search?q=XyzNotFound")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0


@pytest.mark.asyncio
async def test_search_query_too_short(client: AsyncClient, seed_geography):
    response = await client.get("/api/search?q=A")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_search_special_characters(client: AsyncClient, seed_geography):
    response = await client.get("/api/search?q=Antananarivo%20%3B%20DROP")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["results"], dict)
