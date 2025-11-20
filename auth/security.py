from __future__ import annotations

from typing import Optional


class AuthError(Exception):
    """Base auth-related error."""


class InvalidTokenError(AuthError):
    """Raised when a provided token is invalid or malformed."""


def extract_bearer(auth_header: Optional[str]) -> Optional[str]:
    """Extract token from Authorization header in the form 'Bearer <token>'."""
    if not auth_header:
        return None
    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None
    return parts[1]
