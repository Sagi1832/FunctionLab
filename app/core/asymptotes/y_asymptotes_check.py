from __future__ import annotations
from typing import Dict, Optional
import sympy as sp

def horizontal_asymptotes(f: sp.Expr, x: sp.Symbol) -> Dict[str, Optional[sp.Expr]]:
    # x -> +oo
    try:
        Lp = sp.limit(f, x, sp.oo)
    except Exception:
        Lp = None

    # x -> -oo
    try:
        Lm = sp.limit(f, x, -sp.oo)
    except Exception:
        Lm = None

    return {
        "left":  _finite_scalar_or_none(Lm),
        "right": _finite_scalar_or_none(Lp),
    }

def _finite_scalar_or_none(v: Optional[sp.Expr]) -> Optional[sp.Expr]:
    if v is None:
        return None

    # אם קיבלנו Limit שלא בוצע – נבצע אותו
    try:
        if isinstance(v, sp.Limit):
            v = v.doit()
    except Exception:
        return None

    # פישוט עדין
    try:
        v = sp.simplify(v)
    except Exception:
        pass

    # סינון ערכים לא סופיים/לא ממשיים/טווחים/צברים
    if any(v.has(s) for s in (sp.oo, -sp.oo, sp.zoo, sp.nan)):
        return None
    if isinstance(v, (sp.Set, sp.Interval, sp.AccumBounds)):
        return None
    if getattr(v, "is_finite", None) is False:
        return None
    if getattr(v, "is_real", None) is False:
        return None

    # החזרה כמספר/ביטוי מפושט סופי
    try:
        return sp.nsimplify(v)
    except Exception:
        return v

