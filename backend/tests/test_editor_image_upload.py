"""Non-regression tests for the editor image upload endpoint (US1).

Ensures POST /api/admin/upload/image keeps the @editorjs/image contract:
- field name `image`
- response payload `{"success": 1, "file": {"url": ...}}`
- auth enforced (Bearer JWT)
- MIME whitelist (jpeg/png/webp/gif)
- 5 MB size cap
"""
import io

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import UserRole
from tests.conftest import create_test_user, get_auth_headers


@pytest_asyncio.fixture
async def editor_headers(client: AsyncClient, db: AsyncSession) -> dict:
    await create_test_user(
        db,
        email="editor-img@pcqvp.mg",
        password="editor12345",
        role=UserRole.editor,
    )
    return await get_auth_headers(client, "editor-img@pcqvp.mg", "editor12345")


def _jpeg_file(size: int = 1024) -> tuple:
    content = b"\xff\xd8\xff\xe0" + b"\x00" * max(0, size - 4)
    return ("image", ("photo.jpg", io.BytesIO(content), "image/jpeg"))


@pytest.mark.asyncio
async def test_editor_image_upload_contract(client: AsyncClient, editor_headers):
    resp = await client.post(
        "/api/admin/upload/image",
        files=[_jpeg_file(2048)],
        headers=editor_headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body.get("success") == 1
    assert "file" in body
    assert body["file"]["url"].startswith("/uploads/images/")


@pytest.mark.asyncio
async def test_editor_image_upload_without_bearer_refused(client: AsyncClient):
    resp = await client.post(
        "/api/admin/upload/image",
        files=[_jpeg_file()],
    )
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_editor_image_upload_rejects_unknown_mime(
    client: AsyncClient, editor_headers
):
    resp = await client.post(
        "/api/admin/upload/image",
        files=[("image", ("picture.heic", io.BytesIO(b"xxxx"), "image/heic"))],
        headers=editor_headers,
    )
    assert resp.status_code in (400, 415)


@pytest.mark.asyncio
async def test_editor_image_upload_rejects_too_large(
    client: AsyncClient, editor_headers
):
    big = 6 * 1024 * 1024
    content = b"\xff\xd8\xff\xe0" + b"\x00" * big
    resp = await client.post(
        "/api/admin/upload/image",
        files=[("image", ("big.jpg", io.BytesIO(content), "image/jpeg"))],
        headers=editor_headers,
    )
    assert resp.status_code == 413
