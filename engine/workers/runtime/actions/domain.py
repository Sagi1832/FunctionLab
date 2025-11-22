from __future__ import annotations

from typing import Any, Dict

import sympy as sp
from app.utils.adapters import sympy_locals
from app.core.foundation.domain import compute_domain


async def _handle_domain(payload: Dict[str, Any]) -> Dict[str, Any]:
    expr_str = payload.get("expr")
    if not expr_str:
        raise ValueError("payload missing 'expr'")

    var_name = payload.get("var", "x")

    try:
        x = sp.Symbol(var_name, real=True)
        locals_map = sympy_locals(var_name, x)
        expr = sp.sympify(expr_str, locals=locals_map)
    except Exception as exc:
        raise ValueError(f"invalid expression: {exc}") from exc

    dom = compute_domain(expr, x)
    return {"raw": sp.sstr(dom)}
