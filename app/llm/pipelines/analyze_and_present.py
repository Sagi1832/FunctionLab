# app/llm/pipelines/analyze_and_present.py
from __future__ import annotations
from typing import List
import logging
from app.llm.schemas.analyze import AnalyzeRequest, AnalyzeResult, AnalyzeResponse


from .analyze_present_helpers import (
    preflight_validate,
    normalize_input,
    run_core_action,
    build_analyze_result,
    build_raw_only_response,
    generate_presentation,
    maybe_add_narration,
    build_final_response,
)

logger = logging.getLogger(__name__)

class MissingParamsError(ValueError):
    """Raised when a required parameter for the requested action is missing."""

def _preflight_validate(req: AnalyzeRequest) -> List[str]:
    """Local shim to keep old name; delegates to helpers.preflight_validate."""
    return preflight_validate(req)

def analyze_and_present(req: AnalyzeRequest) -> AnalyzeResponse:
    """Analyze and present the request."""
    missing = _preflight_validate(req)
    if missing:
        raise MissingParamsError("; ".join(missing))

    expr, var, _norm = normalize_input(req)

    report = run_core_action(req, expr, var)

    result: AnalyzeResult = build_analyze_result(req, expr, var, report)

    if not req.present:
        payload = build_raw_only_response(result)
        return AnalyzeResponse(**payload)

    present_data, extra_warnings = generate_presentation(req, result)
    result.warnings.extend(extra_warnings)

    present_data = maybe_add_narration(req, present_data, result.warnings)

    payload = build_final_response(result, present_data)
    return AnalyzeResponse(**payload)
