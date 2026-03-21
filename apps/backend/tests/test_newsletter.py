import pytest
from httpx import AsyncClient

from app.services.newsletter_service import generate_confirm_token


@pytest.mark.asyncio
async def test_subscribe(client: AsyncClient):
    response = await client.post(
        "/api/newsletter/subscribe",
        json={"email": "test@example.com"},
    )
    assert response.status_code == 200
    assert "confirmation" in response.json()["message"].lower()


@pytest.mark.asyncio
async def test_subscribe_invalid_email(client: AsyncClient):
    response = await client.post(
        "/api/newsletter/subscribe",
        json={"email": "not-an-email"},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_confirm_valid_token(client: AsyncClient):
    # Subscribe first
    await client.post(
        "/api/newsletter/subscribe",
        json={"email": "confirm@example.com"},
    )
    token = generate_confirm_token("confirm@example.com")
    response = await client.get(
        f"/api/newsletter/confirm?token={token}",
        follow_redirects=False,
    )
    assert response.status_code == 302
    assert "confirmed" in response.headers["location"]


@pytest.mark.asyncio
async def test_confirm_invalid_token(client: AsyncClient):
    response = await client.get(
        "/api/newsletter/confirm?token=invalid-token",
        follow_redirects=False,
    )
    assert response.status_code == 302
    assert "error=invalid" in response.headers["location"]


@pytest.mark.asyncio
async def test_subscribe_duplicate(client: AsyncClient):
    await client.post(
        "/api/newsletter/subscribe",
        json={"email": "dup@example.com"},
    )
    # Confirm
    token = generate_confirm_token("dup@example.com")
    await client.get(f"/api/newsletter/confirm?token={token}", follow_redirects=False)

    # Subscribe again
    response = await client.post(
        "/api/newsletter/subscribe",
        json={"email": "dup@example.com"},
    )
    assert response.status_code == 200
    assert "deja inscrit" in response.json()["message"].lower()
