from __future__ import annotations
from typing import Optional, Tuple, Any
from app.llm.schemas.analyze import Action
from app.llm.providers.api_client import APIClient


def dispatch_action(
    action: Action,
    *,
    expr: Any,
    var: str,
    interval: Optional[Tuple[float, float]] = None,
    closed: Optional[Tuple[bool, bool]] = None,
):
    """Dispatch the action to the API client."""
    client = APIClient()

    if action == Action.domain:
        return client.domain(expr=expr, var=var)

    if action == Action.derivative:
        return client.derivative(expr=expr, var=var)

    if action == Action.x_intercepts:
        return client.x_intercepts(expr=expr, var=var)

    if action == Action.y_intercepts:
        return client.y_intercepts(expr=expr, var=var)

    if action == Action.asymptotes_and_holes:
        return client.asymptotes_and_holes(expr=expr, var=var)

    if action == Action.extrema_and_monotonic:
        return client.extrema_and_monotonic(expr=expr, var=var, interval=interval, closed=closed)

    """Raise an error for an unsupported action."""
    raise ValueError(f"Unsupported action: {action}")
