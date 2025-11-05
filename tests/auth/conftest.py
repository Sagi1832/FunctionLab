# tests/auth/conftest.py
"""
Async test fixtures with SAVEPOINT-based isolation.
- Session-scoped engine + clean schema on startup
- Per-test: single DB connection, outer transaction, nested SAVEPOINT
- Reopen SAVEPOINT after each commit to keep tests isolated
"""
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import event
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.main import app
from app.config.settings import settings
from app.db.base import Base
from app.db.session import get_db
from app.auth import models as _  # noqa: F401  (register models)


def _as_asyncpg_url(database_url: str) -> str:
    from sqlalchemy.engine.url import make_url
    url = make_url(database_url)
    if url.get_backend_name().startswith("postgresql+"):
        return database_url
    if url.get_backend_name() == "postgresql":
        return str(url.set(drivername="postgresql+asyncpg"))
    return database_url


ASYNC_TEST_DB_URL = _as_asyncpg_url(settings.TEST_DATABASE_URL)


# ---------- Session-scoped engine (+ clean schema once) ----------
@pytest.fixture(scope="session")
async def engine() -> AsyncEngine:
    eng = create_async_engine(ASYNC_TEST_DB_URL, future=True, pool_pre_ping=True)
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all, checkfirst=True)
        await conn.run_sync(Base.metadata.create_all, checkfirst=True)
    try:
        yield eng
    finally:
        await eng.dispose()


# ---------- Per-test DB session with nested transaction ----------
@pytest.fixture
async def db_session(engine: AsyncEngine) -> AsyncSession:
    """
    One physical connection per test, outer transaction + SAVEPOINT.
    Any commit() in app code will 'release' the savepoint; we immediately
    open a new one so the test can keep committing safely.
    """
    # One dedicated connection for the test
    conn = await engine.connect()
    # Begin outer transaction (rolled back at test end)
    outer_tx = await conn.begin()

    # Bind session to the same connection
    SessionLocal = async_sessionmaker(bind=conn, class_=AsyncSession, expire_on_commit=False)
    session = SessionLocal()

    # First SAVEPOINT
    nested_tx = await session.begin_nested()

    # Re-open SAVEPOINT after each commit on the nested transaction
    @event.listens_for(session.sync_session, "after_transaction_end")
    def _restart_savepoint(sync_session, trans):  # noqa: N802 (sqlalchemy API)
        if trans.nested and not sync_session.in_nested_transaction():
            sync_session.begin_nested()

    try:
        yield session
    finally:
        # Clean up in strict order
        await session.close()
        await outer_tx.rollback()
        await conn.close()


# ---------- FastAPI client using the same test session ----------
@pytest.fixture
async def client(db_session: AsyncSession):
    async def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac
    finally:
        app.dependency_overrides.clear()
