"""Logging configuration utilities for the engine service."""

from __future__ import annotations

import logging
import os


def configure_logging(default_level: str = "INFO") -> None:
    """Configure basic logging for the engine worker."""
    level = os.getenv("LOG_LEVEL", default_level).upper()
    logging.basicConfig(
        level=getattr(logging, level, logging.INFO),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

