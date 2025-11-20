from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Dict, Optional

from engine.kafka.config import KafkaSettings
from engine.kafka.consumer import EngineRequestConsumer
from engine.kafka.producer import EngineResponseProducer


@dataclass(slots=True)
class KafkaRuntime:
    """Holds running Kafka components and the consumer task."""
    settings: KafkaSettings
    producer: EngineResponseProducer
    consumer: EngineRequestConsumer
    _consumer_task: Optional[asyncio.Task[None]] = None

    async def wait(self) -> None:
        """Wait for the consumer loop to finish."""
        if self._consumer_task is not None:
            await self._consumer_task


async def start_kafka_runtime(
    handlers: Dict[str, Callable[[Dict[str, Any]], Awaitable[Dict[str, Any]]]],
    *,
    broker_url: str | None = None,
    request_topic: str | None = None,
    response_topic: str | None = None,
) -> KafkaRuntime:
    """Start the Kafka runtime."""
    settings = KafkaSettings()
    if broker_url is not None:
        settings.broker_url = broker_url
    if request_topic is not None:
        settings.request_topic = request_topic
    if response_topic is not None:
        settings.response_topic = response_topic
    
    producer = EngineResponseProducer(settings)
    consumer = EngineRequestConsumer(settings, producer=producer, handlers=handlers)

    await producer.start()
    await consumer.start()

    runtime = KafkaRuntime(settings=settings, producer=producer, consumer=consumer)
    runtime._consumer_task = asyncio.create_task(consumer.run())
    return runtime


async def stop_kafka_runtime(runtime: KafkaRuntime) -> None:
    """Stop the consume loop and shutdown Kafka components."""
    # Cancel the consumer task if it's still running
    if runtime._consumer_task is not None:
        runtime._consumer_task.cancel()
        try:
            await runtime._consumer_task
        except asyncio.CancelledError:
            pass
        runtime._consumer_task = None

    await runtime.consumer.stop()
    await runtime.producer.stop()

