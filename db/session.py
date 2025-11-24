from __future__ import annotations
import logging
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.engine.url import make_url
from config.settings import settings

logger = logging.getLogger(__name__)

def _mask_password(url: str) -> str:
    """Mask password in database URL for logging."""
    from sqlalchemy.engine.url import make_url as parse_url
    parsed = parse_url(url)
    if parsed.password:
        return url.replace(f":{parsed.password}@", ":***@")
    return url


# Use DATABASE_URL from settings (single source of truth)
_raw_url = settings.DATABASE_URL
_temp_parsed = make_url(_raw_url.replace("postgresql+asyncpg://", "postgresql://"))

_db_host = _temp_parsed.host or "localhost"
_db_port = _temp_parsed.port or 5432
_db_user = _temp_parsed.username or ""
_db_password = _temp_parsed.password or ""
_db_name = _temp_parsed.database.lstrip("/") if _temp_parsed.database else ""

ASYNC_DATABASE_URL: str = f"postgresql+asyncpg://{_db_user}:{_db_password}@{_db_host}:{_db_port}/{_db_name}"

parsed_url = make_url(ASYNC_DATABASE_URL)
# Log DB host (without password) for startup visibility
logger.info("Using DB URL: %s", _mask_password(ASYNC_DATABASE_URL))

engine: AsyncEngine = create_async_engine(
    ASYNC_DATABASE_URL,
    pool_pre_ping=True,
    echo=False,
    pool_recycle=3600,
    pool_size=5,
    max_overflow=10,
)

SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get a database session."""
    session: AsyncSession = SessionLocal()
    try:
        yield session
    except Exception as e:
        error_msg = str(e)
        if "password" in error_msg.lower() or "authentication" in error_msg.lower():
            logger.error(
                f"Database authentication failed. "
                f"Host: {parsed_url.host}, Port: {parsed_url.port}, "
                f"Database: {parsed_url.database}, User: {parsed_url.username}. "
                f"Check that password matches DATABASE_URL."
            )
        await session.rollback()
        raise
    finally:
        await session.close()


