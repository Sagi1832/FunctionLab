from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models.user import User
from app.auth.repositories import (
    create_user,
    get_user_by_username,
    user_exists,
    create_refresh_token as repo_create_refresh,
    get_refresh_by_jti,
    revoke_refresh_token,
)
from app.auth.services.password_service import hash_password, verify_password, is_password_minimal
from app.auth.services.token_service import (
    create_access_token,
    create_refresh_token,
    decode_token,
    new_jti,
)
from app.config.settings import settings


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


async def register(session: AsyncSession, username: str, password: str) -> User:
    """Create a new user if username not taken. Caller must commit."""
    normalized = username.lower()
    if await user_exists(session, normalized):
        raise ValueError("Username already exists")
    if not is_password_minimal(password):
        raise ValueError("Password does not meet minimal requirements")
    user = await create_user(session, normalized, hash_password(password))
    return user


async def login(session: AsyncSession, username: str, password: str) -> Tuple[str, str]:
    """Authenticate and return (access_token, refresh_token). Caller must commit."""
    normalized = username.lower()
    user = await get_user_by_username(session, normalized)
    if user is None or not verify_password(password, user.hashed_password):
        raise ValueError("Invalid credentials")

    jti = new_jti()
    now = _now_utc()
    refresh_expires_at = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    await repo_create_refresh(session, user_id=user.id, jti=jti, expires_at=refresh_expires_at)

    access = create_access_token(sub=user.id)
    refresh = create_refresh_token(sub=user.id, jti=jti)
    return access, refresh


async def refresh(session: AsyncSession, refresh_token: str) -> Tuple[str, str]:
    """Rotate refresh token and return new (access, refresh). Caller must commit."""
    payload = decode_token(refresh_token, verify_type="refresh")
    user_id = int(payload["sub"])  # guaranteed string per token service
    jti = payload.get("jti")
    if not jti:
        raise ValueError("Malformed refresh token")

    token = await get_refresh_by_jti(session, jti)
    if token is None:
        raise ValueError("Refresh token not found")

    now = _now_utc()
    if token.revoked_at is not None or token.expires_at <= now:
        raise ValueError("Refresh token is not active")

    new_id = new_jti()
    new_expires_at = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    await repo_create_refresh(session, user_id=user_id, jti=new_id, expires_at=new_expires_at)
    await revoke_refresh_token(session, jti=jti, revoked_at=now)

    access = create_access_token(sub=user_id)
    refresh_jwt = create_refresh_token(sub=user_id, jti=new_id)
    return access, refresh_jwt


async def logout(session: AsyncSession, refresh_token: str) -> None:
    """Revoke the given refresh token if present. Caller must commit; idempotent."""
    payload = decode_token(refresh_token, verify_type="refresh")
    jti = payload.get("jti")
    if not jti:
        return
    now = _now_utc()
    await revoke_refresh_token(session, jti=jti, revoked_at=now)
