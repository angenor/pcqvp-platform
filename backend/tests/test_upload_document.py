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
        db,
        email="admin-doc@pcqvp.mg",
        password="admin12345",
        role=UserRole.admin,
    )
    return await get_auth_headers(client, "admin-doc@pcqvp.mg", "admin12345")


def _pdf_file(size: int = 1024, name: str = "doc.pdf") -> tuple:
    content = b"%PDF-1.4\n" + b"\x00" * max(0, size - 9)
    return ("document", (name, io.BytesIO(content), "application/pdf"))


@pytest.mark.asyncio
async def test_upload_document_success(client: AsyncClient, admin_headers):
    resp = await client.post(
        "/api/admin/upload/document",
        files=[_pdf_file(2048, "plan.pdf")],
        headers=admin_headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] == 1
    file = body["file"]
    assert file["url"].startswith("/uploads/documents/")
    assert file["url"].endswith(".pdf")
    assert file["mime"] == "application/pdf"
    assert file["name"] == "plan.pdf"
    assert file["size"] == 2048


@pytest.mark.asyncio
async def test_upload_document_rejects_unknown_mime(
    client: AsyncClient, admin_headers
):
    zip_file = ("document", ("a.zip", io.BytesIO(b"PK\x03\x04..."), "application/zip"))
    resp = await client.post(
        "/api/admin/upload/document",
        files=[zip_file],
        headers=admin_headers,
    )
    assert resp.status_code == 415


@pytest.mark.asyncio
async def test_upload_document_rejects_too_large(
    client: AsyncClient, admin_headers
):
    big = 21 * 1024 * 1024
    resp = await client.post(
        "/api/admin/upload/document",
        files=[_pdf_file(big, "big.pdf")],
        headers=admin_headers,
    )
    assert resp.status_code == 413


@pytest.mark.asyncio
async def test_upload_document_requires_auth(client: AsyncClient):
    resp = await client.post(
        "/api/admin/upload/document", files=[_pdf_file(512)]
    )
    assert resp.status_code in (401, 403)
