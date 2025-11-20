# Lifecycle helpers (startup/shutdown hooks) for the API package.

from .startup import on_startup, on_shutdown, engine_client

__all__ = ["on_startup", "on_shutdown", "engine_client"]
