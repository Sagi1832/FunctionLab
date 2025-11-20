from __future__ import annotations

import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from api.kafka.topics import REQUEST_TOPIC, RESPONSE_TOPIC

class KafkaSettings(BaseSettings):
    """Kafka configuration for the API side."""
    broker_url: str = os.getenv("ENGINE_KAFKA_BOOTSTRAP", "functionlab-kafka:9092")
    client_id: str = "functionlab-api"
    group_id: str = "fl.api"
    request_topic: str = os.getenv("ENGINE_REQUEST_TOPIC", REQUEST_TOPIC)
    response_topic: str = os.getenv("ENGINE_RESPONSE_TOPIC", RESPONSE_TOPIC)
    security_protocol: str = "PLAINTEXT"
    sasl_mechanism: str = ""
    sasl_username: str = ""
    sasl_password: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="KAFKA_",
        extra="ignore",
    )

