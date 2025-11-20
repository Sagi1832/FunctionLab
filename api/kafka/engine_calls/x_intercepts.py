from typing import Any, Optional, Tuple
from api.lifecycle import engine_client

async def call_x_intercepts(
    expr: str,
    var: str = "x",
    interval: Optional[Tuple[float, float]] = None,
    closed: Optional[Tuple[bool, bool]] = None,
) -> dict[str, Any]:
    """Call engine via Kafka to find x-intercepts."""
    payload = {
        "expr": expr,
        "var": var,
    }
    if interval is not None:
        payload["interval"] = list(interval)
    if closed is not None:
        payload["closed"] = list(closed)
    result = await engine_client.call_engine(
        action="x_intercepts",
        payload=payload,
    )
    return result