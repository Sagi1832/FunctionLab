from fastapi import FastAPI
from api.kafka import EngineKafkaClient

engine_client = EngineKafkaClient()

async def on_startup(app: FastAPI) -> None:
    """Initialize Kafka client on FastAPI startup."""
    await engine_client.start()
    app.state.engine_kafka_client = engine_client


async def on_shutdown(app: FastAPI) -> None:
    """Gracefully stop Kafka client on FastAPI shutdown."""
    await engine_client.stop()
    app.state.engine_kafka_client = None
