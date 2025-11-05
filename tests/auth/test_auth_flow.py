"""
Auth flow tests for the FastAPI authentication system.

Tests the complete authentication flow including registration, login, token refresh,
protected endpoint access, logout, and various error scenarios.
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_login_and_access_protected(client: AsyncClient):
    """Happy-path test: complete auth flow from registration to logout."""
    username = "testuser_happy"
    password = "securepass123"

    # 1) Attempt to access protected endpoint without auth -> 401
    r = await client.get("/auth/me")
    assert r.status_code == 401, f"Expected 401, got {r.status_code}: {r.text}"

    # 2) Register new user -> 201
    r = await client.post("/auth/register", json={"username": username, "password": password})
    assert r.status_code == 201, f"Expected 201, got {r.status_code}: {r.text}"
    reg_data = r.json()
    assert reg_data["username"] == username.lower()
    assert "id" in reg_data
    assert "created_at" in reg_data

    # 3) Login -> 200, receive access and refresh tokens
    r = await client.post("/auth/login", json={"username": username, "password": password})
    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
    login_data = r.json()
    access = login_data["access_token"]
    refresh = login_data["refresh_token"]
    assert access and refresh, "Expected both tokens"
    assert len(access) > 10  # JWT should be substantial

    # 4) Access protected endpoint with access token -> 200
    r = await client.get("/auth/me", headers={"Authorization": f"Bearer {access}"})
    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
    me_data = r.json()
    assert me_data["username"] == username.lower(), "Username should be lowercased"
    assert me_data["id"] == reg_data["id"], "User ID should match"

    # 5) Refresh tokens -> 200, new tokens different from old
    r = await client.post("/auth/refresh", json={"refresh_token": refresh})
    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
    refresh_data = r.json()
    new_access = refresh_data["access_token"]
    new_refresh = refresh_data["refresh_token"]
    assert new_access != access, "New access token should differ"
    assert new_refresh != refresh, "New refresh token should differ"

    # 6) Access protected endpoint with new access token -> 200
    r = await client.get("/auth/me", headers={"Authorization": f"Bearer {new_access}"})
    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
    assert r.json()["username"] == username.lower()

    # 7) Logout -> 204
    r = await client.post("/auth/logout", json={"refresh_token": new_refresh})
    assert r.status_code == 204, f"Expected 204, got {r.status_code}: {r.text}"

    # 8) Attempt refresh with revoked token -> 401
    r = await client.post("/auth/refresh", json={"refresh_token": new_refresh})
    assert r.status_code == 401, f"Expected 401, got {r.status_code}: {r.text}"


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    """Negative test: login with incorrect password -> 401."""
    username = "testuser_badpass"
    password = "correctpass123"

    # Register user
    r = await client.post("/auth/register", json={"username": username, "password": password})
    assert r.status_code == 201

    # Try login with wrong password
    r = await client.post("/auth/login", json={"username": username, "password": "wrongpass123"})
    assert r.status_code == 401, f"Expected 401, got {r.status_code}: {r.text}"


@pytest.mark.asyncio
async def test_register_duplicate_username(client: AsyncClient):
    """Negative test: register duplicate username (case-insensitive) -> 409."""
    username = "TestUser_Case"
    password = "pass123456"

    # Register first time
    r = await client.post("/auth/register", json={"username": username, "password": password})
    assert r.status_code == 201

    # Try register again with same username -> 409
    r = await client.post("/auth/register", json={"username": username, "password": password})
    assert r.status_code == 409, f"Expected 409, got {r.status_code}: {r.text}"

    # Try register with different case -> should also fail due to case-insensitive check
    r = await client.post("/auth/register", json={"username": username.upper(), "password": password})
    assert r.status_code == 409, f"Expected 409 for case variation, got {r.status_code}: {r.text}"


@pytest.mark.asyncio
async def test_access_protected_without_auth(client: AsyncClient):
    """Negative test: access protected endpoint without Authorization header -> 401."""
    r = await client.get("/auth/me")
    assert r.status_code == 401, f"Expected 401, got {r.status_code}: {r.text}"

    # Try with malformed header
    r = await client.get("/auth/me", headers={"Authorization": "InvalidToken"})
    assert r.status_code == 401, f"Expected 401 for malformed auth, got {r.status_code}: {r.text}"


@pytest.mark.asyncio
async def test_refresh_with_invalid_token(client: AsyncClient):
    """Negative test: refresh with malformed/expired token -> 401."""
    # Try refresh with garbage token
    r = await client.post("/auth/refresh", json={"refresh_token": "invalid.jwt.token.here"})
    assert r.status_code == 401, f"Expected 401, got {r.status_code}: {r.text}"

    # Try refresh with empty token
    r = await client.post("/auth/refresh", json={"refresh_token": ""})
    assert r.status_code == 422, f"Expected 422 for empty token, got {r.status_code}: {r.text}"


@pytest.mark.asyncio
async def test_register_short_password(client: AsyncClient):
    """Negative test: register with password < 6 chars -> 400."""
    r = await client.post("/auth/register", json={"username": "testuser", "password": "123"})
    assert r.status_code == 422, f"Expected 422 for short password, got {r.status_code}: {r.text}"


@pytest.mark.asyncio
async def test_login_nonexistent_user(client: AsyncClient):
    """Negative test: login with nonexistent username -> 401."""
    r = await client.post("/auth/login", json={"username": "nonexistent_user_xyz", "password": "doesntmatter"})
    assert r.status_code == 401, f"Expected 401, got {r.status_code}: {r.text}"
