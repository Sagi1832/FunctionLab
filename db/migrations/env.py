import asyncio
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context
from config.settings import settings
from db.base import Base
from sqlalchemy.engine.url import make_url


from auth import models  # noqa: F401



config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    raw_url = settings.DATABASE_URL
    url_str = raw_url.replace("postgresql+asyncpg://", "postgresql://")
    url_obj = make_url(url_str)
    _db_host = url_obj.host or "localhost"
    _db_port = url_obj.port or 5432
    _db_user = url_obj.username or ""
    _db_password = url_obj.password or ""
    _db_name = url_obj.database.lstrip("/") if url_obj.database else ""
    url = f"postgresql+asyncpg://{_db_user}:{_db_password}@{_db_host}:{_db_port}/{_db_name}"
    config.set_main_option("sqlalchemy.url", url)
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Run migrations on a connection."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run asynchronous migrations."""
    raw_url = settings.DATABASE_URL
    url_str = raw_url.replace("postgresql+asyncpg://", "postgresql://")
    url_obj = make_url(url_str)
    _db_host = url_obj.host or "localhost"
    _db_port = url_obj.port or 5432
    _db_user = url_obj.username or ""
    _db_password = url_obj.password or ""
    _db_name = url_obj.database.lstrip("/") if url_obj.database else ""
    reconstructed_url = f"postgresql+asyncpg://{_db_user}:{_db_password}@{_db_host}:{_db_port}/{_db_name}"
    config.set_main_option("sqlalchemy.url", reconstructed_url)

    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
