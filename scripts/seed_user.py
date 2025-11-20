from __future__ import annotations

import asyncio
import os
import sys

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.engine.url import make_url
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from app.auth.services.password_service import hash_password

DEFAULT_USERNAME = "sagi1234"
DEFAULT_PASSWORD = "FunctionLab123!"


def _build_engine(url: str) -> tuple[Engine | AsyncEngine, bool]:
    parsed = make_url(url)
    backend = parsed.get_backend_name()
    driver = parsed.get_driver_name()
    print(f"Using backend={backend}, driver={driver}")
    is_async = driver in {"asyncpg", "aiosqlite"}
    if is_async:
        return create_async_engine(url), True
    return create_engine(url), False


DELETE_STMT = text("DELETE FROM users WHERE lower(username) = :username_lower")
INSERT_STMT = text(
    """
    INSERT INTO users (username, hashed_password)
    VALUES (:username, :hashed_password)
    RETURNING id;
    """
)


async def _seed_async(engine: AsyncEngine, delete_payload, insert_payload) -> int:
    async with engine.begin() as conn:
        await conn.execute(DELETE_STMT, delete_payload)
        result = await conn.execute(INSERT_STMT, insert_payload)
        row = result.scalar_one()
    await engine.dispose()
    return row


def _seed_sync(engine: Engine, delete_payload, insert_payload) -> int:
    with engine.begin() as conn:
        conn.execute(DELETE_STMT, delete_payload)
        result = conn.execute(INSERT_STMT, insert_payload)
        row = result.scalar_one()
    engine.dispose()
    return row


def main() -> int:
    load_dotenv()

    url = os.getenv("SQLALCHEMY_DATABASE_URL") or os.getenv("DATABASE_URL")
    if not url:
        print("ERROR: SQLALCHEMY_DATABASE_URL (or DATABASE_URL) is not set.", file=sys.stderr)
        return 1

    username = os.getenv("SEED_USER_USERNAME", DEFAULT_USERNAME).strip().lower()
    password = os.getenv("SEED_USER_PASSWORD", DEFAULT_PASSWORD)
    hashed = hash_password(password)

    try:
        engine, is_async = _build_engine(url)
        delete_payload = {"username_lower": username}
        insert_payload = {"username": username, "hashed_password": hashed}
        if is_async:
            user_id = asyncio.run(_seed_async(engine, delete_payload, insert_payload))
        else:
            user_id = _seed_sync(engine, delete_payload, insert_payload)
        print(f"Seed user ready: username={username}, id={user_id}")
        return 0
    except Exception as exc:
        import traceback

        traceback.print_exc()
        print(f"ERROR: {exc!r}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

