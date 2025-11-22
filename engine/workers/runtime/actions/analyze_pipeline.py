from __future__ import annotations

import logging
from typing import Any, Dict

from app.llm.schemas.analyze import AnalyzeRequest, AnalyzeResponse, Action, AnalyzeResult
from app.llm.schemas.normalization import NormalizationRequest
from app.llm.agents.input_normalizer_agent.input_normalizer import InputNormalizer
from app.llm.agents.presenter_llm.agent import LLMPresenter
from engine.workers.runtime.actions.actions_fallback import _FALLBACK_BUILDERS

logger = logging.getLogger(__name__)


async def run_engine_analyze_pipeline(
    request: AnalyzeRequest,
    math_handler: callable,
) -> AnalyzeResponse:
    """Run the engine analyze pipeline."""
    warnings: list[str] = []
    errors: list[str] = []
    
    # Step 1: Normalize input using InputNormalizer LLM
    try:
        normalizer = InputNormalizer()
        norm_result = normalizer.run(
            NormalizationRequest(raw=request.raw, var=request.var)
        )
        expr_str = norm_result.expr
        var = norm_result.var
    except Exception as exc:
        logger.exception("Input normalization failed")
        errors.append(f"Input normalization failed: {str(exc)}")
        # Fallback: try to use raw as-is
        expr_str = request.raw.replace("^", "**")
        var = request.var
        warnings.append("Used raw input without normalization")
    
    # Step 2: Run calculus core to produce report
    try:
        # Prepare handler payload
        handler_payload: Dict[str, Any] = {
            "expr": expr_str,
            "var": var,
        }
        if request.interval is not None:
            handler_payload["interval"] = request.interval
        if request.closed is not None:
            handler_payload["closed"] = request.closed
        
        # Call the math handler (e.g., _handle_domain, _handle_derivative, etc.)
        report = await math_handler(handler_payload)
    except Exception as exc:
        logger.exception("Calculus core failed")
        errors.append(f"Calculus analysis failed: {str(exc)}")
        # Return error response with fallback present
        return AnalyzeResponse(
            action=request.action,
            expr=expr_str,
            var=var,
            present="Unable to generate explanation due to analysis error.",
            warnings=warnings,
            errors=errors,
        )
    
    # Step 3: Call presenter LLM to generate human-friendly explanation
    present_text = ""
    try:
        # Create AnalyzeResult-like object for presenter (internal use only)
        result_for_presenter = AnalyzeResult(
            action=request.action,
            expr=expr_str,
            var=var,
            report=report,  # Internal report, not exposed in final response
            warnings=warnings,
            errors=errors,
        )
        presenter = LLMPresenter()
        present_text = presenter.run(result_for_presenter)
        
        if not present_text or not present_text.strip():
            warnings.append("LLM presenter returned empty result")
            present_text = "No presentable results were produced."
    except Exception as exc:
        logger.warning("Presenter LLM failed: %s", exc, exc_info=True)
        warnings.append(f"LLM presenter failed: {str(exc)}")
        # Fallback: generate a simple text from the report
        present_text = _generate_fallback_present(request.action, report)
    
    # Ensure present is never empty
    if not present_text or not present_text.strip():
        present_text = "Unable to generate explanation."
    
    # Step 4: Return AnalyzeResponse with present string (no raw report)
    return AnalyzeResponse(
        action=request.action,
        expr=expr_str,
        var=var,
        present=present_text.strip(),
        warnings=warnings,
        errors=errors,
    )


def _generate_fallback_present(action: Action, report: Dict[str, Any]) -> str:
    """Generate a simple fallback text when presenter LLM fails."""
    action_str = action.value
    builder = _FALLBACK_BUILDERS.get(action_str)
    if builder is not None:
        return builder(report)

    return "Analysis completed, but unable to generate explanation."

