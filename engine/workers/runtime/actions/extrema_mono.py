from __future__ import annotations

from typing import Any, Dict, Tuple

import sympy as sp
from app.api.adapters import sympy_locals
from app.core.critical_points.extreme_points import classify_extrema_from_monotonic
from app.core.critical_points.true_critical_candidates import find_critical_candidates_simple
from app.core.foundation.derivative import DerivativeEngine
from app.core.monotonic import monotonicity_intervals
from app.api.all_routes.func_library.extrema_and_mono.helpers import (
    _mk_interval,
    _point_to_str,
    _monotonic_output,
)


async def _handle_extrema_and_monotonic(payload: Dict[str, Any]) -> Dict[str, Any]:
    expr_str = payload.get("expr")
    if not expr_str:
        raise ValueError("payload missing 'expr'")

    var_name = payload.get("var", "x")

    interval_raw: Tuple[float, float] | None = payload.get("interval")
    closed_raw: Tuple[bool, bool] | None = payload.get("closed")
    if interval_raw is None or closed_raw is None:
        raise ValueError("payload missing 'interval' or 'closed'")

    try:
        x = sp.Symbol(var_name, real=True)
        locals_map = sympy_locals(var_name, x)
        expr = sp.sympify(expr_str, locals=locals_map)
    except Exception as exc:
        raise ValueError(f"invalid expression: {exc}") from exc

    interval = _mk_interval(interval_raw, closed_raw)

    engine = DerivativeEngine(expr, x)

    candidates = find_critical_candidates_simple(
        engine.expr,
        x,
        interval=interval,
        require_interval_if_infinite=False,
    )

    mono_pairs = monotonicity_intervals(engine, interval=interval)
    monotonic_map = _monotonic_output(engine, interval)

    classification = classify_extrema_from_monotonic(expr, x, candidates, {seg: str(sign) for seg, sign in mono_pairs})
    extrema = [
        {"point": _point_to_str(x0, y0), "label": label}
        for (x0, y0), label in classification.items()
    ]

    return {
        "monotonic": monotonic_map,
        "extrema": extrema,
    }

