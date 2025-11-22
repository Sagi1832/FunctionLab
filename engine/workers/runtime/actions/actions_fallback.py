from __future__ import annotations
from typing import Any, Dict
from typing import Callable

FallbackBuilder = Callable[[Dict[str, Any]], str]

def _fallback_domain(report: Dict[str, Any]) -> str:
    raw = report.get("raw", "")
    return f"Domain: {raw}" if raw else "Domain: Unable to determine"

def _fallback_derivative(report: Dict[str, Any]) -> str:
    raw = report.get("raw", "")
    return f"Derivative: {raw}" if raw else "Derivative: Unable to compute"

def _fallback_x_intercepts(report: Dict[str, Any]) -> str:
    points = report.get("points", [])
    if points:
        return f"X-intercepts: {', '.join(str(p) for p in points)}"
    return "X-intercepts: None"

def _fallback_y_intercepts(report: Dict[str, Any]) -> str:
    point = report.get("point")
    if point:
        return f"Y-intercept: {point}"
    return "Y-intercept: None"

def _fallback_asymptotes_and_holes(report: Dict[str, Any]) -> str:
    parts: list[str] = []
    vertical = report.get("vertical", [])
    if vertical:
        parts.append(f"Vertical asymptotes: {', '.join(str(v) for v in vertical)}")
    horizontal = report.get("horizontal", {})
    if horizontal:
        parts.append(f"Horizontal asymptotes: {horizontal}")
    holes = report.get("holes", [])
    if holes:
        parts.append(f"Holes: {', '.join(str(h) for h in holes)}")
    return "; ".join(parts) if parts else "Asymptotes and holes: None"

def _fallback_extrema_and_monotonic(report: Dict[str, Any]) -> str:
    parts: list[str] = []
    monotonic = report.get("monotonic", {})
    if monotonic:
        parts.append(f"Monotonicity: {monotonic}")
    extrema = report.get("extrema", [])
    if extrema:
        parts.append(f"Extrema: {extrema}")
    return "; ".join(parts) if parts else "Extrema and monotonicity: Unable to determine"


_FALLBACK_BUILDERS: dict[str, FallbackBuilder] = {
    "domain": _fallback_domain,
    "derivative": _fallback_derivative,
    "x_intercepts": _fallback_x_intercepts,
    "y_intercepts": _fallback_y_intercepts,
    "asymptotes_and_holes": _fallback_asymptotes_and_holes,
    "extrema_and_monotonic": _fallback_extrema_and_monotonic,
}
