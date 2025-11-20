from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

import sympy as sp
from app.api.adapters import sympy_locals, sstr_ln
from app.core.interception.x_interception import x_intercepts


async def _handle_x_intercepts(payload: Dict[str, Any]) -> Dict[str, Any]:
    expr_str = payload.get("expr")
    if not expr_str:
        raise ValueError("payload missing 'expr'")

    var_name = payload.get("var", "x")
    interval_raw: Optional[Tuple[float, float]] = payload.get("interval")
    closed_raw: Optional[Tuple[bool, bool]] = payload.get("closed")

    try:
        x = sp.Symbol(var_name, real=True)
        locals_map = sympy_locals(var_name, x)
        expr = sp.sympify(expr_str, locals=locals_map)
    except Exception as exc:
        raise ValueError(f"invalid input: {exc}") from exc

    interval = None
    if interval_raw is not None:
        a, b = interval_raw
        lc, rc = closed_raw or (True, True)
        interval = sp.Interval(a, b, left_open=not lc, right_open=not rc)

    solutions = x_intercepts(expr, x, interval=interval)
    points = [f"({sstr_ln(sol)}, 0)" for sol in solutions]

    return {"points": points}

