from __future__ import annotations

import asyncio
import logging

from engine.workers.runtime import run_worker

logger = logging.getLogger(__name__)


def main() -> None:
    try:
        asyncio.run(run_worker())
    except KeyboardInterrupt:
        logger.info("Engine worker interrupted by user")


if __name__ == "__main__":
    main()

