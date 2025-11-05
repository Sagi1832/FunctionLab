from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


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


settings = Settings()


