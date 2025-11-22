from __future__ import annotations

from typing import Any, Awaitable, Callable, Dict

from app.llm.schemas.analyze import AnalyzeRequest

from .analyze_pipeline import run_engine_analyze_pipeline

VALID_MATH_ACTIONS = {
    "domain",
    "derivative",
    "asymptotes_and_holes",
    "x_intercepts",
    "y_intercepts",
    "extrema_and_monotonic",
}

async def _handle_analyze_and_present(
    payload: Dict[str, Any],
    handlers: Dict[str, Callable[[Dict[str, Any]], Awaitable[Dict[str, Any]]]],
) -> Dict[str, Any]:
    """Handle analyze_and_present operation."""
    math_action = payload.get("action")
    if not math_action:
        raise ValueError("payload missing 'action' field")
    
    if math_action not in VALID_MATH_ACTIONS:
        raise ValueError(f"unsupported action '{math_action}'")
    
    try:
        request = AnalyzeRequest(**payload)
    except Exception as exc:
        raise ValueError(f"Invalid AnalyzeRequest payload: {exc}") from exc
    
    math_handler = handlers[math_action]
    
    response = await run_engine_analyze_pipeline(request, math_handler)
    
    return response.model_dump()