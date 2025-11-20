import json

from typing import Any, Dict

def to_bytes(payload: Dict[str, Any]) -> bytes:
    return json.dumps(payload).encode("utf-8")

def from_bytes(raw: bytes) -> Dict[str, Any]:
    return json.loads(raw.decode("utf-8"))

