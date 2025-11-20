from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Union, Final
from uuid import uuid4

from jose import jwt

from config.settings import settings


_LEEWAY_SECONDS: Final[int] = 30

def new_jti() -> str:
    """Generate a new token identifier."""
    return str(uuid4())


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _to_str_sub(sub: Union[str, int]) -> str:
    return str(sub)


def create_access_token(*, sub: Union[str, int], extra: Optional[Dict[str, Any]] = None) -> str:
    """Create a signed access JWT with short expiration."""
    now = _now_utc()
    exp = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload: Dict[str, Any] = {
        "sub": _to_str_sub(sub),
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
        "type": "access",
    }
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(
    *, sub: Union[str, int], jti: str, extra: Optional[Dict[str, Any]] = None
) -> str:
    """Create a signed refresh JWT with longer expiration and jti."""
    now = _now_utc()
    exp = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    payload: Dict[str, Any] = {
        "sub": _to_str_sub(sub),
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
        "jti": jti,
        "type": "refresh",
    }
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str, verify_type: Optional[str] = None) -> Dict[str, Any]:
    """Decode and validate a JWT. Optionally assert token type ('access' or 'refresh')."""
    options = {"verify_exp": True, "verify_aud": False}
    if getattr(settings, "JWT_LEEWAY", None):
        options["leeway"] = settings.JWT_LEEWAY  
    else:
        options["leeway"] = _LEEWAY_SECONDS

    payload = jwt.decode(
        token,
        settings.JWT_SECRET,
        algorithms=[settings.JWT_ALGORITHM],
        options=options,
    )
    if verify_type is not None and payload.get("type") != verify_type:
        raise ValueError("Invalid token type")
    return payload
