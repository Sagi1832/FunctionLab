from typing import Any, Awaitable, Callable, Dict

# Valid mathematical actions (excluding "analyze_and_present" which is a Kafka operation name)
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
    """Handle analyze_and_present operation by extracting the actual action from the payload.
    
    This handler extracts the real mathematical action (e.g., "domain", "derivative") from
    the AnalyzeRequest payload and dispatches to the appropriate handler.
    
    The Kafka action is "analyze_and_present", but the actual math action comes from
    payload["action"] and must be one of the valid mathematical actions.
    
    Args:
        payload: The AnalyzeRequest payload containing the math action and data.
        handlers: Dictionary of all available handlers (passed to avoid circular import).
    """
    # Extract the actual math action from the AnalyzeRequest payload
    # This is NOT the Kafka action ("analyze_and_present"), but the user's math action
    math_action = payload.get("action")
    if not math_action:
        raise ValueError("payload missing 'action' field")
    
    # Validate that the action is a supported mathematical action
    # Do NOT validate against "analyze_and_present" - that's the Kafka operation name, not a math action
    if math_action not in VALID_MATH_ACTIONS:
        raise ValueError(f"unsupported action '{math_action}'")
    
    # Prepare the handler payload by converting "raw" to "expr" if needed
    handler_payload: Dict[str, Any] = payload.copy()
    
    # If payload has "raw" but not "expr", use "raw" as "expr"
    if "raw" in handler_payload and "expr" not in handler_payload:
        handler_payload["expr"] = handler_payload["raw"]
    
    # Remove "action" from handler payload since handlers don't need it
    # (they already know what action they're handling)
    handler_payload.pop("action", None)
    
    # Dispatch to the actual math handler using the math action from the payload
    handler = handlers[math_action]
    result = await handler(handler_payload)
    
    return result