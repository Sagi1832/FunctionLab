from __future__ import annotations

from typing import Any, Dict

import sympy as sp
from app.utils.adapters import sstr_ln, sympy_locals
from app.core.foundation.derivative import DerivativeEngine


async def _handle_derivative(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Handle the derivative request."""
    expr_str = payload.get("expr")
    if not expr_str:
        raise ValueError("payload missing 'expr'")

    var_name = payload.get("var", "x")

    try:
        x = sp.Symbol(var_name, real=True)
        locals_map = sympy_locals(var_name, x)
        expr = sp.sympify(expr_str, locals=locals_map)
    except Exception as exc:
        raise ValueError(f"invalid input: {exc}") from exc

    engine = DerivativeEngine(expr, x)
    derivative = engine.simplify_derivative()

    return {"raw": sstr_ln(derivative)}

