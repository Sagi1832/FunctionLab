from __future__ import annotations

from typing import Final

from passlib.context import CryptContext


_pwd_context: Final = CryptContext(schemes=["bcrypt"], deprecated="auto")


def is_password_minimal(plain: str) -> bool:
    """Minimal helper: ensure baseline length. Not a full policy."""
    return len(plain) >= 6


def hash_password(plain: str) -> str:
    """Hash a plaintext password using bcrypt."""
    return _pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """Verify plaintext against a bcrypt hash."""
    return _pwd_context.verify(plain, hashed)


