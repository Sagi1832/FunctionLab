from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict

from engine.kafka.topics import REQUEST_TOPIC, RESPONSE_TOPIC


class KafkaSettings(BaseSettings):
    """Kafka configuration sourced from environment variables."""
    broker_url: str = "functionlab-kafka:9092"
    client_id: str = "functionlab-engine"
    group_id: str = "fl.engine.dev"
    request_topic: str = REQUEST_TOPIC
    response_topic: str = RESPONSE_TOPIC
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

