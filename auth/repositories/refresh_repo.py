from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from auth.models.refresh_token import RefreshToken


async def create(session: AsyncSession, user_id: int, jti: str, expires_at: datetime) -> RefreshToken:
    """Insert a refresh token row. Does not commit; caller manages transaction."""
    token = RefreshToken(user_id=user_id, jti=jti, expires_at=expires_at)
    session.add(token)
    await session.flush()
    return token


async def get_by_jti(session: AsyncSession, jti: str) -> Optional[RefreshToken]:
    """Return refresh token by JTI or None."""
    result = await session.execute(select(RefreshToken).where(RefreshToken.jti == jti))
    return result.scalar_one_or_none()


async def revoke(session: AsyncSession, jti: str, revoked_at: datetime) -> int:
    """Set revoked_at for a specific token by JTI. Returns number of rows affected. No commit."""
    stmt = (
        update(RefreshToken)
        .where(RefreshToken.jti == jti, RefreshToken.revoked_at.is_(None))
        .values(revoked_at=revoked_at)
    )
    result = await session.execute(stmt)
    return result.rowcount or 0


async def revoke_all_for_user(session: AsyncSession, user_id: int, revoked_at: datetime) -> int:
    """Revoke all active tokens for a user. Returns number of rows affected. No commit."""
    stmt = (
        update(RefreshToken)
        .where(RefreshToken.user_id == user_id, RefreshToken.revoked_at.is_(None))
        .values(revoked_at=revoked_at)
    )
    result = await session.execute(stmt)
    return result.rowcount or 0


