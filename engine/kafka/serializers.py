from __future__ import annotations
from typing import Any
import orjson


def to_bytes(payload: Any) -> bytes:
    """Serialize payload to UTF-8 bytes using orjson."""
    return orjson.dumps(payload)


def from_bytes(data: bytes) -> Any:
    """Deserialize bytes produced by :func:`to_bytes`."""
    if data is None:
        return None
    return orjson.loads(data)

