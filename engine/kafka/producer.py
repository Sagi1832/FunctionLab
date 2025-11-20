from __future__ import annotations
import logging
from typing import Optional
from aiokafka import AIOKafkaProducer
from engine.kafka.config import KafkaSettings
from engine.kafka.serializers import to_bytes
from engine.schemas.messages import EngineResponse
from engine.workers.runtime.message_handlers import build_kafka_client_kwargs


logger = logging.getLogger(__name__)
class EngineResponseProducer:
    """Thin wrapper around AIOKafkaProducer for sending EngineResponse messages."""

    def __init__(self, settings: KafkaSettings) -> None:
        self._settings = settings
        self._producer: Optional[AIOKafkaProducer] = None

    async def start(self) -> None:
        """Start the underlying Kafka producer."""
        producer_kwargs, _ = build_kafka_client_kwargs(self._settings)
        self._producer = AIOKafkaProducer(**producer_kwargs)
        await self._producer.start()
        logger.info("EngineResponseProducer started (client_id=%s)", self._settings.client_id)

    async def stop(self) -> None:
        """Stop the underlying Kafka producer."""
        if self._producer is not None:
            await self._producer.stop()
            self._producer = None
            logger.info("EngineResponseProducer stopped")

    async def send_response(self, response: EngineResponse, *, topic: str) -> None:
        """Encode and publish an EngineResponse to the given topic."""
        if self._producer is None:
            raise RuntimeError("Producer not started. Call start() first.")
        await self._producer.send_and_wait(topic, to_bytes(response.model_dump()))
        logger.info(
            "Produced response to topic=%s: correlation_id=%s, ok=%s",
            topic,
            response.correlation_id,
            response.ok,
        )


