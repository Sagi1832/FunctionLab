"""Kafka runtime loop for the engine worker."""

from __future__ import annotations
       
import logging
from engine.common.logging import configure_logging
from engine.kafka.lifecycle import start_kafka_runtime, stop_kafka_runtime
from engine.workers.runtime.message_handlers import HANDLERS


logger = logging.getLogger(__name__)




async def run_worker() -> None:
    """Public entrypoint that runs the engine worker."""
    configure_logging()
    logger.info("Starting Kafka worker loop...")
    runtime = await start_kafka_runtime(handlers=HANDLERS)

    try:
        logger.info("Engine worker started and ready to consume messages")
        await runtime.wait()
    finally:
        await stop_kafka_runtime(runtime)
        logger.info("Engine worker stopped")


