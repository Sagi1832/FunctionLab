"""Test for analyze_and_present Kafka handler to ensure it uses payload action, not Kafka action."""

from __future__ import annotations

import pytest
from engine.workers.runtime.actions.analyze_and_present import _handle_analyze_and_present


@pytest.mark.asyncio
async def test_analyze_and_present_uses_payload_action_not_kafka_action():
    """Test that analyze_and_present handler extracts math action from payload, not Kafka action.
    
    This test simulates a Kafka call with:
    - Kafka action: "analyze_and_present" (engine function name)
    - Payload action: "domain" (user's math action)
    
    The handler should extract "domain" from payload["action"] and dispatch to the domain handler,
    not treat "analyze_and_present" as the math action.
    """
    # Simulate the payload that comes from AnalyzeRequest
    payload = {
        "raw": "1/x",
        "var": "x",
        "action": "domain",  # This is the math action, NOT "analyze_and_present"
        "present": True,
    }
    
    # This should NOT raise "unsupported action 'analyze_and_present'"
    # It should extract "domain" from payload["action"] and dispatch to domain handler
    result = await _handle_analyze_and_present(payload)
    
    # Verify we got a result (domain handler returns {"raw": "..."})
    assert result is not None
    assert "raw" in result
    assert isinstance(result["raw"], str)


@pytest.mark.asyncio
async def test_analyze_and_present_rejects_invalid_math_action():
    """Test that analyze_and_present handler rejects invalid math actions from payload."""
    payload = {
        "raw": "1/x",
        "var": "x",
        "action": "invalid_action",  # Invalid math action
        "present": True,
    }
    
    # Should raise error about the invalid math action, not about "analyze_and_present"
    with pytest.raises(ValueError, match="unsupported action 'invalid_action'"):
        await _handle_analyze_and_present(payload)


@pytest.mark.asyncio
async def test_analyze_and_present_requires_action_in_payload():
    """Test that analyze_and_present handler requires action field in payload."""
    payload = {
        "raw": "1/x",
        "var": "x",
        # Missing "action" field
        "present": True,
    }
    
    with pytest.raises(ValueError, match="payload missing 'action' field"):
        await _handle_analyze_and_present(payload)


@pytest.mark.asyncio
async def test_analyze_and_present_converts_raw_to_expr():
    """Test that analyze_and_present handler converts 'raw' to 'expr' for handlers."""
    payload = {
        "raw": "x**2",  # Only "raw", no "expr"
        "var": "x",
        "action": "domain",
        "present": True,
    }
    
    # Should work - handler converts "raw" to "expr"
    result = await _handle_analyze_and_present(payload)
    assert result is not None
    assert "raw" in result

