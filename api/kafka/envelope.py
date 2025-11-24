from __future__ import annotations

import time
import uuid
from typing import Any, Dict
from api.kafka.schemas import EngineRequest, EngineResponse
from api.kafka.serializers import to_bytes, from_bytes

def make_engine_request(
    *,
    action: str,
    payload: Dict[str, Any],
    correlation_id: str | None = None,
    reply_to: str | None = None,
) -> EngineRequest:
    """Create an EngineRequest with a fresh correlation_id and timestamp."""
    if correlation_id is None:
        correlation_id = uuid.uuid4().hex
    if reply_to is None:
        raise ValueError("reply_to topic must be provided")
    return EngineRequest(
        action=action,
        payload=payload,
        correlation_id=correlation_id,
        reply_to=reply_to,
        ts=int(time.time()),
    )

def encode_engine_request(request: EngineRequest) -> bytes:
    """Serialize EngineRequest → bytes for Kafka."""
    return to_bytes(request.model_dump())

def decode_engine_response(raw: bytes) -> EngineResponse:
    """Deserialize Kafka bytes → EngineResponse."""
    data = from_bytes(raw)
    return EngineResponse(**data)

