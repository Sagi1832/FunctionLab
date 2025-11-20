from __future__ import annotations

"""Kafka topic names for API-to-engine communication.

These must match the topic names defined in the engine repository.
"""

REQUEST_TOPIC = "fl.request"
RESPONSE_TOPIC = "fl.response"

__all__ = ["REQUEST_TOPIC", "RESPONSE_TOPIC"]

