# app/llm/pipelines/analyze_present_helpers.py
from __future__ import annotations
from typing import List, Tuple, Dict, Any, Optional
import logging

from app.llm.schemas.analyze import AnalyzeRequest, AnalyzeResult, Action
from app.llm.schemas.normalization import NormalizationRequest, NormalizationResult
from app.llm.agents.input_normalizer_agent.input_normalizer import InputNormalizer
from app.llm.agents.narrator_agent.narrator import NarratorAgent
from app.llm.pipelines.dispatch import dispatch_action

# helpers (internal) – moved to a dedicated support module
from app.llm.pipelines.analyze_present_backend.analyze_present_support import (
    _init_present_data,
    _attach_asymptotes_card,
    _attach_extrema_card,
    _maybe_run_presenter,
)

logger = logging.getLogger(__name__)

# ---------- Validation ----------

def preflight_validate(req: AnalyzeRequest) -> List[str]:
    """Collect missing-parameter errors for the requested action."""
    errors: List[str] = []
    if req.action == Action.extrema_and_monotonic and req.interval is None:
        errors.append("The action 'extrema_and_monotonic' requires interval (e.g. [a, b]).")
    return errors

# ---------- Normalization ----------

def normalize_input(req: AnalyzeRequest) -> Tuple[Any, str, NormalizationResult]:
    """Run the input normalizer and return (expr, var, norm)."""
    normalizer = InputNormalizer()
    norm: NormalizationResult = normalizer.run(
        NormalizationRequest(raw=req.raw, var=req.var)
    )
    return norm.expr, norm.var, norm

# ---------- Core analysis ----------

def run_core_action(req: AnalyzeRequest, expr: Any, var: str) -> Dict[str, Any]:
    """Dispatch the math action and return the analysis report."""
    return dispatch_action(
        req.action,
        expr=expr,
        var=var,
        interval=req.interval,
        closed=req.closed,
    )

def build_analyze_result(req: AnalyzeRequest, expr: Any, var: str, report: Dict[str, Any]) -> AnalyzeResult:
    """Create the AnalyzeResult DTO (warnings/errors start empty)."""
    return AnalyzeResult(
        action=req.action,
        expr=str(expr),
        var=var,
        report=report,
        warnings=[],
        errors=[],
    )

# ---------- Raw-only response ----------

def build_raw_only_response(result: AnalyzeResult) -> Dict[str, Any]:
    """Return dict payload for AnalyzeResponse when present=False."""
    return {
        "action": result.action,
        "expr": result.expr,
        "var": result.var,
        "report": result.report,
        "warnings": result.warnings,
        "errors": result.errors,
        "present": None,
    }

# ---------- Presentation (code / llm) ----------

def generate_presentation(req: AnalyzeRequest, result: AnalyzeResult) -> Tuple[Optional[Dict[str, Any]], List[str]]:
    """Generate presenter output and attach it to the present data (refactored)."""
    warnings: List[str] = []

    present: Dict[str, Any] = _init_present_data(result)

    if result.action.value == "asymptotes_and_holes":
        _attach_asymptotes_card(present, result)

    if result.action.value == "extrema_and_monotonic":
        _attach_extrema_card(present, result)
    else:
        present.setdefault("card", {})
        _maybe_run_presenter(present, result, warnings)

    return present, warnings

# ---------- Optional narration ----------

def maybe_add_narration(
    req: AnalyzeRequest,
    present_data: Optional[Dict[str, Any]],
    warnings_out: List[str]
) -> Optional[Dict[str, Any]]:
    """If narrate=True and present data exists, try to add a natural-language narration."""
    if not (req.narrate and present_data):
        return present_data
    try:
        narrator = NarratorAgent()
        narration = narrator.run(present_data, req.narrate_lang)
        if narration:
            present_data["narration"] = narration
        else:
            warn = "Narrator failed: Could not generate natural language summary"
            logger.warning(warn)
            warnings_out.append(warn)
    except Exception as e:
        warn = f"Narrator failed: {str(e)}"
        logger.warning(warn)
        warnings_out.append(warn)
    return present_data

# ---------- Final response builder ----------

def build_final_response(result: AnalyzeResult, present_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Create dict for AnalyzeResponse construction."""
    return {
        "action": result.action,
        "expr": result.expr,
        "var": result.var,
        "report": result.report,
        "warnings": result.warnings,
        "errors": result.errors,
        "present": present_data,
    }
