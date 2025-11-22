from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

import sympy as sp
from app.utils.adapters import sympy_locals
from app.core.asymptotes.asymptotes_display import asymptotes_summary


async def _handle_asymptotes_and_holes(payload: Dict[str, Any]) -> Dict[str, Any]:
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
        raise ValueError(f"invalid expression: {exc}") from exc

    interval = None
    if interval_raw is not None:
        a, b = interval_raw
        lc, rc = closed_raw or (True, True)
        interval = sp.Interval(a, b, left_open=not lc, right_open=not rc)

    summary = asymptotes_summary(expr, x, interval=interval)

    vertical = [sp.sstr(v) for v in summary.get("vertical", [])]
    horizontal_in = summary.get("horizontal") or {}
    horizontal = {
        "left": None if horizontal_in.get("left") is None else sp.sstr(horizontal_in["left"]),
        "right": None if horizontal_in.get("right") is None else sp.sstr(horizontal_in["right"]),
    }
    holes = [
        f"({sp.sstr(x0)}, {sp.sstr(y0)})"
        for (x0, y0) in summary.get("holes", [])
    ]

    return {
        "vertical": vertical,
        "horizontal": horizontal,
        "holes": holes,
    }

