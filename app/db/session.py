from __future__ import annotations
import logging
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.engine.url import make_url, URL
from app.config.settings import settings

logger = logging.getLogger(__name__)

def _as_asyncpg_url(database_url: str) -> str:
    """Convert a synchronous database URL to an asynchronous one."""
    url = make_url(database_url)
    if url.get_backend_name().startswith("postgresql+"):
        if "+asyncpg" not in url.get_backend_name():
            async_url: URL = url.set(drivername="postgresql+asyncpg")
            return str(async_url)
        return database_url
    if url.get_backend_name() == "postgresql":
        async_url: URL = url.set(drivername="postgresql+asyncpg")
        return str(async_url)
    return database_url


def _mask_password(url: str) -> str:
    """Mask password in database URL for logging."""
    from sqlalchemy.engine.url import make_url as parse_url
    parsed = parse_url(url)
    if parsed.password:
        return url.replace(f":{parsed.password}@", ":***@")
    return url


_raw_url = settings.DATABASE_URL
_temp_parsed = make_url(_raw_url.replace("postgresql+asyncpg://", "postgresql://"))

_db_host = _temp_parsed.host or "localhost"
_db_port = _temp_parsed.port or 5432
_db_user = _temp_parsed.username or ""
_db_password = _temp_parsed.password or ""
_db_name = _temp_parsed.database.lstrip("/") if _temp_parsed.database else ""

ASYNC_DATABASE_URL: str = f"postgresql+asyncpg://{_db_user}:{_db_password}@{_db_host}:{_db_port}/{_db_name}"

parsed_url = make_url(ASYNC_DATABASE_URL)
logger.info("Database connection configuration:")
logger.info("  Source: settings.DATABASE_URL")
logger.info(f"  Full URL (masked): {_mask_password(ASYNC_DATABASE_URL)}")
logger.info(f"  Driver: {parsed_url.get_backend_name()}")
logger.info(f"  Host: {parsed_url.host}")
logger.info(f"  Port: {parsed_url.port}")
logger.info(f"  Database: {parsed_url.database}")
logger.info(f"  Username: {parsed_url.username}")
logger.info(f"  Password: {'***' if parsed_url.password else 'None'}")

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


