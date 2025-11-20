from typing import Any, Tuple
from api.lifecycle import engine_client

async def call_extrema_and_monotonic(
    expr: str,
    var: str,
    interval: Tuple[float, float],
    closed: Tuple[bool, bool] = (True, True),
) -> dict[str, Any]:
    """Call engine via Kafka to compute extrema and monotonicity."""
    payload = {
        "expr": expr,
        "var": var,
        "interval": list(interval),
        "closed": list(closed),
    }
    result = await engine_client.call_engine(
        action="extrema_and_monotonic",
        payload=payload,
    )
    return result