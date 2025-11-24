from __future__ import annotations
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class EngineRequest(BaseModel):
    """Envelope for requests sent from the API to the engine over Kafka."""
    action: str = Field(..., description="Requested engine action, e.g. 'domain'.")
    payload: Dict[str, Any] = Field(
        default_factory=dict,
        description="Action-specific payload (expr, var, interval, etc.)",
    )
    correlation_id: str = Field(
        ...,
        description="Identifier that ties request and response together.",
    )
    reply_to: str = Field(
        ...,
        description="Kafka topic the engine should publish the response to.",
    )
    ts: int = Field(
        ...,
        description="Unix timestamp emitted by the caller.",
    )
class EngineResponse(BaseModel):
    """Envelope returned by the engine worker over Kafka."""
    correlation_id: str = Field(
        ...,
        description="Matches the originating request.correlation_id.",
    )
    ok: bool = Field(..., description="True when the action succeeded.")
    data: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Payload on success.",
    )
    error: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Error information on failure (message, etc.).",
    )
    ts: int = Field(
        ...,
        description="Unix timestamp when the response was produced.",
    )

