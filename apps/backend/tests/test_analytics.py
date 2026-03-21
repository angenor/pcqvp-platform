import uuid

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import UserRole
from app.models.visit_log import VisitLog
from tests.conftest import create_test_user, get_auth_headers


@pytest_asyncio.fixture
async def admin_headers(db: AsyncSession, client: AsyncClient):
    await create_test_user(db, email="admin@test.com", password="password123", role=UserRole.admin)
    return await get_auth_headers(client, email="admin@test.com", password="password123")


@pytest_asyncio.fixture
async def seed_visits(db: AsyncSession):
    visits = [
        VisitLog(event_type="page_view", path="/", page_type="home"),
        VisitLog(event_type="page_view", path="/communes/123", page_type="commune"),
        VisitLog(event_type="download", path="/api/export", download_format="xlsx"),
    ]
    db.add_all(visits)
    await db.commit()


@pytest.mark.asyncio
async def test_dashboard(client: AsyncClient, admin_headers, seed_visits):
    response = await client.get(
        "/api/admin/analytics/dashboard?period=30d",
        headers=admin_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["period"] == "30d"
    assert data["visits"]["total"] >= 2
    assert data["downloads"]["total"] >= 1


@pytest.mark.asyncio
async def test_dashboard_requires_auth(client: AsyncClient, seed_visits):
    response = await client.get("/api/admin/analytics/dashboard")
    assert response.status_code == 403 or response.status_code == 401
