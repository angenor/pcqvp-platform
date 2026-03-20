import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import UserRole
from tests.conftest import create_test_user, get_auth_headers


@pytest_asyncio.fixture
async def admin_user(db: AsyncSession):
    return await create_test_user(
        db, email="admin@test.com", password="admin12345", role=UserRole.admin
    )


@pytest_asyncio.fixture
async def editor_user(db: AsyncSession):
    return await create_test_user(
        db, email="editor@test.com", password="editor12345", role=UserRole.editor
    )


@pytest_asyncio.fixture
async def inactive_user(db: AsyncSession):
    return await create_test_user(
        db,
        email="inactive@test.com",
        password="inactive123",
        role=UserRole.editor,
        is_active=False,
    )


class TestLogin:
    @pytest.mark.asyncio
    async def test_login_success(self, client: AsyncClient, admin_user):
        response = await client.post(
            "/api/auth/login",
            json={"email": "admin@test.com", "password": "admin12345"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "refresh_token" in response.cookies

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client: AsyncClient, admin_user):
        response = await client.post(
            "/api/auth/login",
            json={"email": "admin@test.com", "password": "wrongpassword"},
        )
        assert response.status_code == 401
        assert response.json()["detail"] == "Identifiants incorrects"

    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, client: AsyncClient):
        response = await client.post(
            "/api/auth/login",
            json={"email": "nobody@test.com", "password": "password123"},
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_login_inactive_account(self, client: AsyncClient, inactive_user):
        response = await client.post(
            "/api/auth/login",
            json={"email": "inactive@test.com", "password": "inactive123"},
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_login_brute_force_lockout(self, client: AsyncClient, admin_user):
        for _ in range(5):
            await client.post(
                "/api/auth/login",
                json={"email": "admin@test.com", "password": "wrongpassword"},
            )

        response = await client.post(
            "/api/auth/login",
            json={"email": "admin@test.com", "password": "admin12345"},
        )
        assert response.status_code == 423


class TestMe:
    @pytest.mark.asyncio
    async def test_me_authenticated(self, client: AsyncClient, admin_user):
        headers = await get_auth_headers(
            client, email="admin@test.com", password="admin12345"
        )
        response = await client.get("/api/auth/me", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "admin@test.com"
        assert data["role"] == "admin"

    @pytest.mark.asyncio
    async def test_me_unauthenticated(self, client: AsyncClient):
        response = await client.get("/api/auth/me")
        assert response.status_code == 403


class TestRegister:
    @pytest.mark.asyncio
    async def test_register_as_admin(self, client: AsyncClient, admin_user):
        headers = await get_auth_headers(
            client, email="admin@test.com", password="admin12345"
        )
        response = await client.post(
            "/api/auth/register",
            json={
                "email": "newuser@test.com",
                "password": "newuser123",
                "role": "editor",
            },
            headers=headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@test.com"
        assert data["role"] == "editor"

    @pytest.mark.asyncio
    async def test_register_as_editor_forbidden(
        self, client: AsyncClient, editor_user
    ):
        headers = await get_auth_headers(
            client, email="editor@test.com", password="editor12345"
        )
        response = await client.post(
            "/api/auth/register",
            json={
                "email": "newuser@test.com",
                "password": "newuser123",
                "role": "editor",
            },
            headers=headers,
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, client: AsyncClient, admin_user):
        headers = await get_auth_headers(
            client, email="admin@test.com", password="admin12345"
        )
        response = await client.post(
            "/api/auth/register",
            json={
                "email": "admin@test.com",
                "password": "password123",
                "role": "editor",
            },
            headers=headers,
        )
        assert response.status_code == 400


class TestRefresh:
    @pytest.mark.asyncio
    async def test_refresh_token_flow(self, client: AsyncClient, admin_user):
        login_response = await client.post(
            "/api/auth/login",
            json={"email": "admin@test.com", "password": "admin12345"},
        )
        assert login_response.status_code == 200

        refresh_response = await client.post("/api/auth/refresh")
        assert refresh_response.status_code == 200
        data = refresh_response.json()
        assert "access_token" in data

    @pytest.mark.asyncio
    async def test_refresh_without_cookie(self, client: AsyncClient):
        response = await client.post("/api/auth/refresh")
        assert response.status_code == 401
