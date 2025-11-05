# app/llm/agents/presenter_llm/presenter_helpers.py
from __future__ import annotations
from typing import Dict, Any, List
from app.llm.utils.mathfmt import fmt_value
from app.llm.utils.intervals import drop_outer_ranges

def _build_base(payload) -> Dict[str, Any]:
    """Fields common to all actions."""
    return {
        "action": payload.action.value,
        "expr": payload.expr,
        "var": payload.var,
        "warnings": payload.warnings,
        "errors": payload.errors,
    }

def _format_extrema_and_monotonic(report: Dict[str, Any]) -> Dict[str, Any]:
    """Prepare monotonicity (with trimming) and extrema."""
    monotonic = report.get("monotonic", {}) or {}
    trimmed = drop_outer_ranges(monotonic)

    formatted_monotonic: Dict[str, Any] = {}
    for interval, behavior in trimmed.items():
        formatted_monotonic[fmt_value(interval)] = behavior

    return {
        "monotonic": formatted_monotonic,
        "extrema": report.get("extrema", []) or [],
    }

def _format_domain(report: Dict[str, Any]) -> Dict[str, Any]:
    raw_domain = report.get("raw", "")
    return {"domain": fmt_value(raw_domain)}

def _format_derivative(report: Dict[str, Any]) -> Dict[str, Any]:
    raw_derivative = report.get("raw", "")
    return {"derivative": fmt_value(raw_derivative)}

def _format_limits(report: Dict[str, Any]) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for key, value in (report or {}).items():
        if value is not None:
            out[key] = fmt_value(value)
    return {"limits": out}

def _format_asymptotes_and_holes(report: Dict[str, Any]) -> Dict[str, Any]:
    out: Dict[str, Any] = {}

    vertical: List[Any] = report.get("vertical", []) or []
    if vertical:
        out["vertical"] = [fmt_value(v) for v in vertical]

    horizontal: Dict[str, Any] = report.get("horizontal", {}) or {}
    if horizontal:
        h_fmt: Dict[str, Any] = {}
        for side, val in horizontal.items():
            if val is not None:
                h_fmt[side] = fmt_value(val)
        if h_fmt:
            out["horizontal"] = h_fmt

    holes: List[Any] = report.get("holes", []) or []
    if holes:
        out["holes"] = [fmt_value(h) for h in holes]

    return {"asymptotes": out}

def _format_intercepts(report: Dict[str, Any], axis: str) -> Dict[str, Any]:
    if axis == "x":
        pts = report.get("points", []) or []
        return {"x_intercepts": [fmt_value(p) for p in pts]} if pts else {}
    # axis == "y"
    p = report.get("point")
    return {"y_intercept": fmt_value(p)} if p is not None else {}

def prepare_analysis_data(payload) -> Dict[str, Any]:
    """Prepare analysis data in a compact, LLM-friendly shape from raw analysis."""
    data = _build_base(payload)
    action = payload.action.value
    report = payload.report or {}

    if action == "extrema_and_monotonic":
        data.update(_format_extrema_and_monotonic(report))

    elif action == "domain":
        data.update(_format_domain(report))

    elif action == "derivative":
        data.update(_format_derivative(report))

    elif action == "limits":
        data.update(_format_limits(report))

    elif action == "asymptotes_and_holes":
        data.update(_format_asymptotes_and_holes(report))

    elif action in ("x_intercepts", "y_intercepts"):
        axis = "x" if action == "x_intercepts" else "y"
        data.update(_format_intercepts(report, axis))

    return data