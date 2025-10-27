from __future__ import annotations
from typing import Dict, Iterable, Literal, Optional, Tuple
import sympy as sp

# ----- type aliases -----
Trend = Literal["inc", "dec", "const"]
Label = Literal["min", "max", "saddle"]
MonoMap = Dict[sp.Interval, str]  # values will be normalized to Trend

# =========================
# main API
# =========================

def classify_extrema_from_monotonic(
    f: sp.Expr,
    x: sp.Symbol,
    candidates: Iterable[sp.Expr],
    monotonicity_map: MonoMap,
    *,
    tol: float = 1e-10,
) -> Dict[Tuple[sp.Expr, sp.Expr], Label]:
    """ Classifies extrema from monotonicity information. """
    out: Dict[Tuple[sp.Expr, sp.Expr], Label] = {}

    for c in candidates:
        c = sp.nsimplify(c)

        # 1) y-value must be real & finite
        y = _finite_real_value(f, x, c)
        if y is None:
            continue

        # 2) pull side-trends from the map
        left, right = _side_trends(c, monotonicity_map, tol=tol)

        # 3) decide label
        lab = _label_from_trends(left, right)

        out[(c, y)] = lab

    return out


# =========================
# small, focused helpers
# =========================

def _canon_trend(s: str) -> Trend:
    """Normalize any monotonicity string to one of: 'inc' | 'dec' | 'const'."""
    s = str(s).strip().lower()
    if s in {"inc", "increasing", "up", "+"}:
        return "inc"
    if s in {"dec", "decreasing", "down", "-"}:
        return "dec"
    return "const"

def _eq(a: sp.Expr, b: sp.Expr, tol: float = 1e-10) -> bool:
    """Robust equality check for SymPy objects (tries numeric and symbolic)."""
    try:
        av = float(sp.N(a))
        bv = float(sp.N(b))
        return abs(av - bv) <= tol
    except Exception:
        return sp.simplify(a - b) == 0

def _is_real_finite(y: sp.Expr) -> bool:
    """True only if y הוא ממשי וסופי."""
    # אם SymPy כבר יודע:
    if getattr(y, "is_real", None) is False:
        return False
    if getattr(y, "is_finite", None) is False:
        return False

    # נסיון סימבולי: חלק מדומה חייב להתאפס
    if getattr(y, "is_real", None) is None:
        if sp.simplify(sp.im(y)) != 0:
            return False

    # נסיון נומרי + פסילת ∞/NaN
    try:
        y_num = sp.N(y)
        if y_num in (sp.oo, -sp.oo, sp.zoo) or y_num.has(sp.nan):
            return False
        if getattr(y_num, "is_real", None) is False:
            return False
    except Exception:
        return False

    return True

def _finite_real_value(f: sp.Expr, x: sp.Symbol, c: sp.Expr) -> Optional[sp.Expr]:
    """Evaluate f(c); return simplified y only if it's real & finite, else None."""
    try:
        y = sp.simplify(f.subs(x, c))
    except Exception:
        return None
    return sp.nsimplify(y) if _is_real_finite(y) else None

def _side_trends(
    point: sp.Expr,
    mono_map: MonoMap,
    *,
    tol: float = 1e-10,
) -> Tuple[Optional[Trend], Optional[Trend]]:
    """ Extract the monotonicity immediately to the left and right of `point` from a map {Interval -> 'inc'/'dec'/'const'}. """
    left: Optional[Trend] = None
    right: Optional[Trend] = None

    for iv, raw in mono_map.items():
        tr = _canon_trend(raw)
        if left is None and _eq(iv.end, point, tol):
            left = tr
        if right is None and _eq(iv.start, point, tol):
            right = tr
        if left is not None and right is not None:
            break

    return left, right

def _label_from_trends(left: Optional[Trend], right: Optional[Trend]) -> Label:
    """ Decide label by comparing the side-trends. """
    if left == "inc" and right == "dec":
        return "max"
    if left == "dec" and right == "inc":
        return "min"
    return "saddle"


