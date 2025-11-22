from __future__ import annotations

import asyncio
import logging
import os
from typing import Any, Dict
from api.kafka.config import KafkaSettings
from api.kafka.envelope import (
    make_engine_request,
)
from api.kafka.schemas import EngineResponse
from api.kafka.producer import EngineRequestProducer
from api.kafka.consumer import EngineResponseConsumer

logger = logging.getLogger(__name__)

class EngineCallError(RuntimeError):
    """Raised when an engine call returns ok=False."""
    pass


class EngineOverloadedError(RuntimeError):
    """Raised when too many concurrent engine calls are in-flight."""
    pass

class EngineKafkaClient:
    """Async Kafka client for calling the engine service from the API."""

    def __init__(self, settings: KafkaSettings | None = None) -> None:
        self._settings: KafkaSettings = settings or KafkaSettings()
        self._producer: EngineRequestProducer | None = None
        self._consumer: EngineResponseConsumer | None = None
        self._pending: dict[str, asyncio.Future[EngineResponse]] = {}
        self._max_concurrent: int = 1000

    async def start(self) -> None:
        """Start producer + consumer components."""
        # Log the effective bootstrap servers
        logger.info("Kafka bootstrap servers: %s", self._settings.broker_url)

        self._producer = EngineRequestProducer(self._settings)
        self._consumer = EngineResponseConsumer(self._settings, self._pending)

        await self._producer.start()
        await self._consumer.start()

        logger.info(
            "EngineKafkaClient started (client_id=%s, request_topic=%s, response_topic=%s)",
            self._settings.client_id,
            self._settings.request_topic,
            self._settings.response_topic,
        )

    async def stop(self) -> None:
        """Stop producer + consumer components."""
        if self._consumer is not None:
            await self._consumer.stop()
            self._consumer = None

        if self._producer is not None:
            await self._producer.stop()
            self._producer = None

        logger.info("EngineKafkaClient stopped")

    async def call_engine(
        self,
        *,
        action: str,
        payload: Dict[str, Any],
        timeout: float | None = None,
    ) -> Dict[str, Any]:
        """Send a request to the engine and wait for the response."""
        if self._producer is None or self._consumer is None:
            raise RuntimeError("EngineKafkaClient not started. Call start() first.")

        # Use ENGINE_RPC_TIMEOUT_SECONDS from env if timeout not specified
        if timeout is None:
            timeout = float(os.getenv("ENGINE_RPC_TIMEOUT_SECONDS", "15"))

        # Check concurrency limit before creating the request
        if len(self._pending) >= self._max_concurrent:
            raise EngineOverloadedError("engine is overloaded (too many concurrent requests)")

        request = make_engine_request(
            action=action,
            payload=payload,
            reply_to=self._settings.response_topic,
        )

        logger.info(
            "Sending request to Kafka: action=%s, correlation_id=%s, reply_to=%s",
            action,
            request.correlation_id,
            request.reply_to,
        )

        fut: asyncio.Future[EngineResponse] = asyncio.Future()
        self._pending[request.correlation_id] = fut

        try:
            await self._producer.send_request(request)

            response = await asyncio.wait_for(fut, timeout=timeout)

            logger.info(
                "Received response from Kafka: correlation_id=%s, ok=%s",
                response.correlation_id,
                response.ok,
            )

            if not response.ok:
                msg = "Engine call failed"
                if response.error and isinstance(response.error, dict):
                    msg = response.error.get("message", msg)
                raise EngineCallError(msg)

            return response.data or {}
        except asyncio.TimeoutError:
            self._pending.pop(request.correlation_id, None)
            logger.warning(
                "Request timeout: action=%s, correlation_id=%s, timeout=%s",
                action,
                request.correlation_id,
                timeout,
            )
            raise
        except Exception as e:
            self._pending.pop(request.correlation_id, None)
            logger.error(
                "Error in call_engine: action=%s, correlation_id=%s, error=%s",
                action,
                request.correlation_id,
                str(e),
                exc_info=True,
            )
            raise
