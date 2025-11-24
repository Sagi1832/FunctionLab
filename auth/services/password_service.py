from __future__ import annotations

from typing import Final

from passlib.context import CryptContext


MIN_PASSWORD_LEN: Final[int] = 6

_pwd_context: Final[CryptContext] = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


def is_password_minimal(plain: str) -> bool:
    """Return True if password meets the minimal policy (length >= 6)."""
    return len(plain) >= MIN_PASSWORD_LEN


def hash_password(plain: str) -> str:
    """
    Hash a plaintext password using bcrypt.
    Only enforces the minimal length rule.
    """
    if not is_password_minimal(plain):
        raise ValueError(f"Password must be at least {MIN_PASSWORD_LEN} characters long.")
    return _pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """
    Verify plaintext against a bcrypt hash.
    No extra validation here – just bcrypt verify.
    """
    return _pwd_context.verify(plain, hashed)
