from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class KafkaSettings(BaseSettings):
    """Kafka configuration for the API side."""

    # Broker URL – read from ENGINE_KAFKA_BOOTSTRAP with a sane default
    broker_url: str = Field(
        default="localhost:9093",  # default for host dev; .env overrides
        env="ENGINE_KAFKA_BOOTSTRAP",
    )

    client_id: str = "fl.api"
    group_id: str = "fl.api"

    request_topic: str = Field(
        default="fl.request.domain",
        env="ENGINE_REQUEST_TOPIC",
    )

    response_topic: str = Field(
        default="fl.response",
        env="ENGINE_RESPONSE_TOPIC",
    )

    security_protocol: str = "PLAINTEXT"
    sasl_mechanism: str = ""
    sasl_username: str = ""
    sasl_password: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


__all__ = ["KafkaSettings"]

