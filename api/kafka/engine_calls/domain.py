from typing import Any
from api.lifecycle import engine_client


async def call_domain(
    expr: str,
    var: str = "x",
) -> dict[str, Any]:
    """Call engine via Kafka to compute function domain."""
    payload = {
        "expr": expr,
        "var": var,
    }
    result = await engine_client.call_engine(
        action="domain",
        payload=payload,
    )
    return result