from __future__ import annotations

import time
import uuid
from typing import Any

from engine.kafka.serializers import from_bytes, to_bytes
from engine.schemas.messages import EngineRequest, EngineResponse


def make_engine_request(
    action: str,
    payload: dict[str, Any],
    *,
    correlation_id: str | None = None,
    reply_to: str | None = None,
) -> EngineRequest:
    """Make an EngineRequest."""
    if correlation_id is None:
        correlation_id = uuid.uuid4().hex

    return EngineRequest(
        action=action,
        payload=payload,
        correlation_id=correlation_id,
        reply_to=reply_to,
        ts=int(time.time()),
    )


def encode_engine_request(request: EngineRequest) -> bytes:
    """Encode an EngineRequest to bytes."""
    return to_bytes(request.model_dump())


def decode_engine_response(raw: bytes) -> EngineResponse:
    """Decode bytes to an EngineResponse."""
    data = from_bytes(raw)
    return EngineResponse.model_validate(data)
