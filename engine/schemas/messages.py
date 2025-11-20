"""Pydantic models for engine request and response payloads."""

from __future__ import annotations

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from engine.kafka.topics import RESPONSE_TOPIC


class EngineRequest(BaseModel):
    """Envelope for incoming Kafka messages targeting the engine."""

    action: str = Field(..., description="Requested engine action, e.g. 'domain'.")
    payload: Dict[str, Any] = Field(default_factory=dict)
    correlation_id: str = Field(..., description="Identifier that ties request/response together.")
    reply_to: str = Field(RESPONSE_TOPIC, description="Topic to publish the response to.")
    ts: int = Field(..., description="Unix timestamp emitted by the caller.")


class EngineResponse(BaseModel):
    """Envelope returned by the engine worker."""

    correlation_id: str = Field(..., description="Matches the originating request.")
    ok: bool = Field(..., description="True when the action succeeded.")
    data: Optional[Dict[str, Any]] = Field(default=None, description="Payload on success.")
    error: Optional[Dict[str, Any]] = Field(default=None, description="Error information on failure.")
    ts: int = Field(..., description="Unix timestamp when the response was produced.")

