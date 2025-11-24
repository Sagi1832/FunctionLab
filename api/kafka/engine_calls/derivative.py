from typing import Any
from api.lifecycle import engine_client

async def call_derivative(
    expr: str,
    var: str = "x",
) -> dict[str, Any]:
    """Call engine via Kafka to compute derivative."""
    payload = {
        "expr": expr,
        "var": var,
    }
    result = await engine_client.call_engine(
        action="derivative",
        payload=payload,
    )
    return result