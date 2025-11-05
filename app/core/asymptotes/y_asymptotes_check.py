from __future__ import annotations
from typing import Dict, Optional
import sympy as sp

def horizontal_asymptotes(f: sp.Expr, x: sp.Symbol) -> Dict[str, Optional[sp.Expr]]:
    """Returns the horizontal asymptotes of the function f(x)."""
    try:
        Lp = sp.limit(f, x, sp.oo)
    except Exception:
        Lp = None

    try:
        Lm = sp.limit(f, x, -sp.oo)
    except Exception:
        Lm = None

    return {
        "left":  _finite_scalar_or_none(Lm),
        "right": _finite_scalar_or_none(Lp),
    }

def _finite_scalar_or_none(v: Optional[sp.Expr]) -> Optional[sp.Expr]:
    """Returns a finite scalar or None."""
    if v is None:
        return None
    try:
        if isinstance(v, sp.Limit):
            v = v.doit()
    except Exception:
        return None
    try:
        v = sp.simplify(v)
    except Exception:
        pass

    if any(v.has(s) for s in (sp.oo, -sp.oo, sp.zoo, sp.nan)):
        return None
    if isinstance(v, (sp.Set, sp.Interval, sp.AccumBounds)):
        return None
    if getattr(v, "is_finite", None) is False:
        return None
    if getattr(v, "is_real", None) is False:
        return None

    try:
        return sp.nsimplify(v)
    except Exception:
        return v

