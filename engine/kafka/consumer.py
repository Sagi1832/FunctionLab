from __future__ import annotations

import logging
from typing import Any, Awaitable, Callable, Dict, Optional

from aiokafka import AIOKafkaConsumer
from pydantic import ValidationError

from engine.kafka.config import KafkaSettings
from engine.schemas.messages import EngineRequest
from engine.workers.runtime.message_handlers import (
	build_kafka_client_kwargs,
	build_response_for_request,
)
from engine.kafka.producer import EngineResponseProducer


logger = logging.getLogger(__name__)
class EngineRequestConsumer:
    """Consumer that reads EngineRequest messages and dispatches to handlers."""

    def __init__(
        self,
        settings: KafkaSettings,
        *,
        producer: EngineResponseProducer,
        handlers: Dict[str, Callable[[Dict[str, Any]], Awaitable[Dict[str, Any]]]],
    ) -> None:
        self._settings = settings
        self._producer = producer
        self._handlers = handlers
        self._consumer: Optional[AIOKafkaConsumer] = None

    async def start(self) -> None:
        """Start the underlying Kafka consumer."""
        _, consumer_kwargs = build_kafka_client_kwargs(self._settings)
        logger.info(
            "Starting EngineRequestConsumer: broker=%s, topic=%s, group_id=%s",
            self._settings.broker_url,
            self._settings.request_topic,
            self._settings.group_id,
        )
        self._consumer = AIOKafkaConsumer(self._settings.request_topic, **consumer_kwargs)
        await self._consumer.start()
        logger.info(
            "EngineRequestConsumer started successfully (group_id=%s, topic=%s)",
            self._settings.group_id,
            self._settings.request_topic,
        )

    async def stop(self) -> None:
        """Stop the underlying Kafka consumer."""
        if self._consumer is not None:
            await self._consumer.stop()
            self._consumer = None
            logger.info("EngineRequestConsumer stopped")

    async def run(self) -> None:
        """Consume loop: decode requests, dispatch, and publish responses."""
        if self._consumer is None:
            raise RuntimeError("Consumer not started. Call start() first.")

        async for message in self._consumer:
            try:
                request = EngineRequest.model_validate_json(message.value)
                logger.info(
                    "Engine received request: action=%s, correlation_id=%s, reply_to=%s",
                    request.action,
                    request.correlation_id,
                    request.reply_to,
                )
            except ValidationError as exc:
                logger.error("Received invalid request payload: %s", exc)
                continue

            try:
                response, reply_topic = await build_response_for_request(
                    request, self._settings, self._handlers
                )
                await self._producer.send_response(response, topic=reply_topic)
                logger.info(
                    "Engine sent response: correlation_id=%s, ok=%s, topic=%s",
                    response.correlation_id,
                    response.ok,
                    reply_topic,
                )
            except Exception:  # noqa: BLE001
                logger.exception("Unhandled error while processing message")


