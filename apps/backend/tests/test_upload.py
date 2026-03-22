import io

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import UserRole
from tests.conftest import create_test_user, get_auth_headers


@pytest_asyncio.fixture
async def admin_headers(client: AsyncClient, db: AsyncSession) -> dict:
    await create_test_user(
        db, email="admin@upload.com", password="admin12345", role=UserRole.admin
    )
    return await get_auth_headers(client, "admin@upload.com", "admin12345")


def _make_image_file(content_type: str = "image/jpeg", size: int = 100) -> tuple:
    """Create a fake image file for testing."""
    content = b"\xff\xd8\xff\xe0" + b"\x00" * (size - 4)
    return ("image", ("test.jpg", io.BytesIO(content), content_type))


class TestUploadImage:
    @pytest.mark.asyncio
    async def test_upload_image_success(
        self, client: AsyncClient, admin_headers
    ):
        file_data = _make_image_file()
        response = await client.post(
            "/api/admin/upload/image",
            files=[file_data],
            headers=admin_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == 1
        assert "file" in data
        assert data["file"]["url"].startswith("/uploads/images/")
        assert data["file"]["url"].endswith(".jpg")

    @pytest.mark.asyncio
    async def test_upload_image_invalid_type(
        self, client: AsyncClient, admin_headers
    ):
        file_data = ("image", ("test.txt", io.BytesIO(b"not an image"), "text/plain"))
        response = await client.post(
            "/api/admin/upload/image",
            files=[file_data],
            headers=admin_headers,
        )
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_upload_image_too_large(
        self, client: AsyncClient, admin_headers
    ):
        # Create a file larger than 5 MB
        large_content = b"\xff\xd8\xff\xe0" + b"\x00" * (6 * 1024 * 1024)
        file_data = (
            "image",
            ("large.jpg", io.BytesIO(large_content), "image/jpeg"),
        )
        response = await client.post(
            "/api/admin/upload/image",
            files=[file_data],
            headers=admin_headers,
        )
        assert response.status_code == 413

    @pytest.mark.asyncio
    async def test_upload_image_no_auth(self, client: AsyncClient):
        file_data = _make_image_file()
        response = await client.post(
            "/api/admin/upload/image",
            files=[file_data],
        )
        assert response.status_code in (401, 403)

    @pytest.mark.asyncio
    async def test_upload_png(self, client: AsyncClient, admin_headers):
        file_data = (
            "image",
            ("test.png", io.BytesIO(b"\x89PNG" + b"\x00" * 100), "image/png"),
        )
        response = await client.post(
            "/api/admin/upload/image",
            files=[file_data],
            headers=admin_headers,
        )
        assert response.status_code == 200
        assert response.json()["file"]["url"].endswith(".png")


class TestUploadImageByUrl:
    @pytest.mark.asyncio
    async def test_upload_by_url_no_auth(self, client: AsyncClient):
        response = await client.post(
            "/api/admin/upload/image-by-url",
            json={"url": "https://example.com/image.jpg"},
        )
        assert response.status_code in (401, 403)
