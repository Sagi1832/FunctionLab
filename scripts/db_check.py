from __future__ import annotations

import os
import sys

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine.url import make_url


def mask_connection_error(exc: Exception) -> str:
    return repr(exc)


def main() -> int:
    load_dotenv()

    url = os.getenv("SQLALCHEMY_DATABASE_URL") or os.getenv("DATABASE_URL")
    if not url:
        print("FAIL: SQLALCHEMY_DATABASE_URL (or DATABASE_URL) not set in environment.", file=sys.stderr)
        return 1

    try:
        parsed = make_url(url)
        host = parsed.host or "None"
        port = parsed.port or "None"
        database = parsed.database or "None"
        driver = parsed.drivername or "None"
        print(f"Config: driver={driver}, host={host}, port={port}, database={database}")
    except Exception as exc:
        print(f"FAIL: Unable to parse database URL: {exc!r}", file=sys.stderr)
        return 1

    engine = create_engine(url)

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        print("PASS: Connected successfully and executed SELECT 1.")
        return 0
    except Exception as exc:
        print(f"FAIL: {mask_connection_error(exc)}", file=sys.stderr)
        return 1
    finally:
        engine.dispose()


if __name__ == "__main__":
    sys.exit(main())

