from __future__ import annotations

import logging
from aiokafka import AIOKafkaProducer
from api.kafka.config import KafkaSettings
from api.kafka.envelope import encode_engine_request
from api.kafka.schemas import EngineRequest

logger = logging.getLogger(__name__)
class EngineRequestProducer:
    """Focused Kafka producer for sending EngineRequest messages."""

    def __init__(self, settings: KafkaSettings) -> None:
        self._settings = settings
        self._producer: AIOKafkaProducer | None = None

    async def start(self) -> None:
        """Initialize and start the underlying AIOKafkaProducer."""
        if self._producer is not None:
            return
        self._producer = AIOKafkaProducer(
            bootstrap_servers=self._settings.broker_url,
            client_id=self._settings.client_id,
        )
        await self._producer.start()
        logger.info("EngineRequestProducer started (client_id=%s, topic=%s)",
                    self._settings.client_id, self._settings.request_topic)

    async def stop(self) -> None:
        """Stop the underlying producer."""
        if self._producer is not None:
            await self._producer.stop()
            self._producer = None
            logger.info("EngineRequestProducer stopped")

    async def send_request(self, request: EngineRequest) -> None:
        """Encode and send the EngineRequest to the request topic."""
        if self._producer is None:
            raise RuntimeError("EngineRequestProducer not started. Call start() first.")
        encoded = encode_engine_request(request)
        await self._producer.send_and_wait(self._settings.request_topic, encoded)
        logger.debug(
            "Successfully sent request to Kafka topic '%s': correlation_id=%s",
            self._settings.request_topic,
            request.correlation_id,
        )

# Deprecated: use EngineKafkaClient instead
