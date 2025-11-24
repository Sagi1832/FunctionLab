from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine.url import make_url

logger = logging.getLogger("app.config")

_CONFIG_LOGGED = False


def _mask_secret(value: Optional[str]) -> str:
    """Mask the secret value."""
    if not value:
        return "None"
    if len(value) <= 4:
        return "***"
    return f"{value[:4]}***"


def _log_env_file_from_settings(conf: "Settings") -> None:
    """Log whether the env file defined on the Settings model exists."""
    env_file = conf.model_config.get("env_file") if hasattr(conf, "model_config") else None
    if env_file:
        env_path = Path(env_file)
        logger.info("Env file '%s' exists: %s", env_path, env_path.exists())
    else:
        logger.info("Env file not configured on Settings.model_config")


def _log_db_url(url_value: str, label: str = "DATABASE_URL") -> None:
    """Parse and log DB connection parts (host/port/name/user) from a URL."""
    try:
        parsed = make_url(url_value)
        logger.info("%s host=%s", label, parsed.host or "None")
        logger.info("%s port=%s", label, parsed.port or "None")
        logger.info("%s name=%s", label, parsed.database or "None")
        logger.info("%s user=%s", label, parsed.username or "None")
    except Exception as exc:
        logger.warning("Unable to parse %s for logging: %s", label, exc)


def _log_primary_db(conf: "Settings") -> None:
    """Log primary async DATABASE_URL info from settings."""
    _log_db_url(conf.DATABASE_URL, "DATABASE_URL")


def _log_sqlalchemy_db_from_env() -> None:
    """If SQLALCHEMY_DATABASE_URL exists in env, log its host/port."""
    sqlalchemy_url = os.getenv("SQLALCHEMY_DATABASE_URL")
    if sqlalchemy_url:
        _log_db_url(sqlalchemy_url, "SQLALCHEMY_DATABASE_URL")
    else:
        logger.info("SQLALCHEMY_DATABASE_URL not set")


def _resolve_env_name() -> str:
    """Pick ENV name from common environment keys."""
    return (
        os.getenv("ENV")
        or os.getenv("APP_ENV")
        or os.getenv("ENVIRONMENT")
        or "undefined"
    )


def _log_environment_banner() -> None:
    """Log basic environment banner (ENV value)."""
    logger.info("ENV=%s", _resolve_env_name())


def _log_openai_config() -> None:
    """Log OpenAI key (masked) and base URL."""
    openai_key = os.getenv("OPENAI_API_KEY")
    logger.info("OPENAI_API_KEY=%s", _mask_secret(openai_key))
    openai_base = os.getenv("OPENAI_BASE_URL") or "None"
    logger.info("OPENAI_BASE_URL=%s", openai_base)


def _log_runtime_configuration(conf: "Settings") -> None:
    """Log runtime configuration."""
    global _CONFIG_LOGGED
    if _CONFIG_LOGGED:
        return

    _log_env_file_from_settings(conf)
    _log_primary_db(conf)
    _log_sqlalchemy_db_from_env()
    _log_environment_banner()
    _log_openai_config()

    _CONFIG_LOGGED = True

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )

    DATABASE_URL: str = Field(..., description="Database URL, prefer postgresql+asyncpg when using async engine")
    TEST_DATABASE_URL: str = Field(..., description="Test database URL")
    JWT_SECRET: str = Field(..., description="JWT secret key")
    JWT_ALGORITHM: str = Field("HS256", description="JWT algorithm, default HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(..., description="Access token TTL in minutes")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(..., description="Refresh token TTL in days")
    OPENAI_API_KEY: Optional[str] = Field(None, description="OpenAI API key for LLM services")
    LLM_MODEL: str = Field("gpt-4o-mini", description="OpenAI model to use for LLM calls")


settings = Settings()

_log_runtime_configuration(settings)


