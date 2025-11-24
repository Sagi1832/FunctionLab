from __future__ import annotations

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.models.user import User


async def get_by_username(session: AsyncSession, username: str) -> Optional[User]:
    """Return user by username (case-insensitive) or None if not found."""
    normalized = username.lower()
    result = await session.execute(select(User).where(User.username == normalized))
    return result.scalar_one_or_none()


async def create(session: AsyncSession, username: str, hashed_password: str) -> User:
    """Create a user (username stored lowercase). Does not commit; caller manages transaction."""
    user = User(username=username, hashed_password=hashed_password)
    session.add(user)
    await session.flush()
    return user


async def exists(session: AsyncSession, username: str) -> bool:
    """Check if a username exists (case-insensitive)."""
    normalized = username.lower()
    result = await session.execute(select(User.id).where(User.username == normalized).limit(1))
    return result.first() is not None


