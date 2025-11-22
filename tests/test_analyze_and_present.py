"""Test for analyze_and_present Kafka handler with new pipeline (normalize -> core -> presenter)."""

from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from engine.workers.runtime.actions.analyze_and_present import _handle_analyze_and_present
from engine.workers.runtime.actions.domain import _handle_domain


@pytest.mark.asyncio
async def test_analyze_and_present_returns_analyze_response_with_present():
    """Test that analyze_and_present handler returns AnalyzeResponse with present string.
    
    The handler should:
    1. Normalize input
    2. Run calculus core
    3. Call presenter LLM
    4. Return AnalyzeResponse with present string (no raw report)
    """
    # Simulate the payload that comes from AnalyzeRequest
    payload = {
        "raw": "x**2",
        "var": "x",
        "action": "domain",
        "present": True,
    }
    
    # Mock handlers dict
    handlers = {
        "domain": _handle_domain,
    }
    
    # Mock the presenter LLM to return a string
    with patch("engine.workers.runtime.actions.analyze_pipeline.LLMPresenter") as mock_presenter_class:
        mock_presenter = MagicMock()
        mock_presenter.run.return_value = "Domain: All real numbers"
        mock_presenter_class.return_value = mock_presenter
        
        # Mock InputNormalizer
        with patch("engine.workers.runtime.actions.analyze_pipeline.InputNormalizer") as mock_normalizer_class:
            mock_normalizer = MagicMock()
            from app.llm.schemas.normalization import NormalizationResult
            mock_normalizer.run.return_value = NormalizationResult(expr="x**2", var="x")
            mock_normalizer_class.return_value = mock_normalizer
            
            result = await _handle_analyze_and_present(payload, handlers)
    
    # Verify we got AnalyzeResponse structure
    assert result is not None
    assert "action" in result
    assert "expr" in result
    assert "var" in result
    assert "present" in result
    assert "warnings" in result
    assert "errors" in result
    
    # Verify present is a non-empty string
    assert isinstance(result["present"], str)
    assert len(result["present"]) > 0
    
    # Verify report is NOT in the response (internal only)
    assert "report" not in result
    
    # Verify action matches
    assert result["action"] == "domain"


@pytest.mark.asyncio
async def test_analyze_and_present_rejects_invalid_math_action():
    """Test that analyze_and_present handler rejects invalid math actions from payload."""
    payload = {
        "raw": "1/x",
        "var": "x",
        "action": "invalid_action",  # Invalid math action
        "present": True,
    }
    
    handlers = {}
    
    # Should raise error about the invalid math action, not about "analyze_and_present"
    with pytest.raises(ValueError, match="unsupported action 'invalid_action'"):
        await _handle_analyze_and_present(payload, handlers)


@pytest.mark.asyncio
async def test_analyze_and_present_requires_action_in_payload():
    """Test that analyze_and_present handler requires action field in payload."""
    payload = {
        "raw": "1/x",
        "var": "x",
        # Missing "action" field
        "present": True,
    }
    
    handlers = {}
    
    with pytest.raises(ValueError, match="payload missing 'action' field"):
        await _handle_analyze_and_present(payload, handlers)


@pytest.mark.asyncio
async def test_analyze_and_present_handles_presenter_failure():
    """Test that analyze_and_present handler handles presenter LLM failures gracefully."""
    payload = {
        "raw": "x**2",
        "var": "x",
        "action": "domain",
        "present": True,
    }
    
    handlers = {
        "domain": _handle_domain,
    }
    
    # Mock presenter to fail
    with patch("engine.workers.runtime.actions.analyze_pipeline.LLMPresenter") as mock_presenter_class:
        mock_presenter = MagicMock()
        mock_presenter.run.side_effect = Exception("LLM API error")
        mock_presenter_class.return_value = mock_presenter
        
        # Mock InputNormalizer
        with patch("engine.workers.runtime.actions.analyze_pipeline.InputNormalizer") as mock_normalizer_class:
            mock_normalizer = MagicMock()
            from app.llm.schemas.normalization import NormalizationResult
            mock_normalizer.run.return_value = NormalizationResult(expr="x**2", var="x")
            mock_normalizer_class.return_value = mock_normalizer
            
            result = await _handle_analyze_and_present(payload, handlers)
    
    # Should still return valid response with fallback present
    assert result is not None
    assert "present" in result
    assert isinstance(result["present"], str)
    assert len(result["present"]) > 0  # Must be non-empty
    assert "report" not in result  # Report not exposed
    
    # Should have warning about presenter failure
    assert len(result.get("warnings", [])) > 0

