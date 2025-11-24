from __future__ import annotations
import asyncio
import logging
from typing import Dict
from aiokafka import AIOKafkaConsumer
from api.kafka.config import KafkaSettings
from api.kafka.envelope import decode_engine_response
from api.kafka.schemas import EngineResponse


logger = logging.getLogger(__name__)
class EngineResponseConsumer:
    """Async Kafka consumer for receiving engine responses."""
    def __init__(
        self,
        settings: KafkaSettings,
        pending: Dict[str, asyncio.Future[EngineResponse]],
    ) -> None:
        self._settings = settings
        self._pending = pending
        self._consumer: AIOKafkaConsumer | None = None
        self._task: asyncio.Task[None] | None = None

    async def start(self) -> None:
        """Start the consumer and background processing task."""
        if self._consumer is not None:
            return
        self._consumer = AIOKafkaConsumer(
            self._settings.response_topic,
            bootstrap_servers=self._settings.broker_url,
            group_id=f"{self._settings.group_id}.api",
            client_id=f"{self._settings.client_id}.api",
            auto_offset_reset="latest",
        )
        await self._consumer.start()
        self._task = asyncio.create_task(self._run())
        logger.info(
            "EngineResponseConsumer started (client_id=%s, topic=%s)",
            self._settings.client_id,
            self._settings.response_topic,
        )

    async def stop(self) -> None:
        """Stop background task and consumer."""
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None

        if self._consumer is not None:
            await self._consumer.stop()
            self._consumer = None
            logger.info("EngineResponseConsumer stopped")

    async def _run(self) -> None:
        """Consume responses and resolve pending futures."""
        assert self._consumer is not None
        consumer = self._consumer
        try:
            async for msg in consumer:
                try:
                    response = decode_engine_response(msg.value)
                    correlation_id = response.correlation_id

                    logger.info(
                        "API received response: correlation_id=%s",
                        correlation_id,
                    )

                    fut = self._pending.pop(correlation_id, None)
                    if fut is not None and not fut.done():
                        logger.info(
                            "Completing future for correlation_id=%s",
                            correlation_id,
                        )
                        fut.set_result(response)
                    else:
                        logger.warning(
                            "Received response for unknown correlation_id=%s",
                            correlation_id,
                        )
                except Exception:
                    logger.exception("Error processing engine response message")
        except asyncio.CancelledError:
            logger.debug("EngineResponseConsumer loop cancelled")
            raise
        except Exception:
            logger.exception("Unexpected error in EngineResponseConsumer loop")

# Internal building block used by EngineKafkaClient.
# This class is not part of the public API - use EngineKafkaClient for Kafka operations.
