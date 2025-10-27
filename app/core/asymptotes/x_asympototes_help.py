# === singular-candidates for general (e.g. tan) ===
import sympy as sp
from typing import List, Optional

def _enumerate_linear_imageset(img: sp.ImageSet, interval: sp.Interval) -> List[sp.Expr]:
    """
    Enumerate ImageSet of the form a*k + b, k ∈ Integers, within interval.
    Works for patterns like pi/2 + k*pi (tan/cos poles).
    """
    lam = img.lamda      # Lambda(k, expr(k))
    k = lam.variables[0]
    expr = sp.simplify(lam.expr)

    # Expect linear in k: expr = a*k + b
    a = sp.simplify(sp.diff(expr, k))
    if a.free_symbols:
        return []  # not linear -> skip
    b = sp.simplify(expr.subs(k, 0))

    # Compute bounds for k so that expr ∈ interval
    L = sp.ceiling((interval.start - b) / a)
    U = sp.floor((interval.end   - b) / a)
    try:
        L_i, U_i = int(L), int(U)
    except Exception:
        return []
    if L_i > U_i:
        return []
    return [sp.simplify(expr.subs(k, n)) for n in range(L_i, U_i + 1)]

def singular_candidates_in_interval(f: sp.Expr, x: sp.Symbol, interval: Optional[sp.Interval]) -> List[sp.Expr]:
    """
    Real singular points of f within interval (if given).
    Uses sympy.calculus.util.singularities and enumerates common ImageSet patterns.
    """
    S = sp.calculus.util.singularities(f, x)          # set of singularities (possibly ImageSet)
    S = sp.Intersection(S, sp.S.Reals)
    if interval is not None:
        S = sp.Intersection(S, interval)

    if isinstance(S, sp.FiniteSet):
        return [sp.simplify(v) for v in S]

    if isinstance(S, sp.ImageSet) and isinstance(interval, sp.Interval):
        return _enumerate_linear_imageset(S, interval)

    # For Unions, try to collect finite parts
    if isinstance(S, sp.Union):
        out: List[sp.Expr] = []
        for part in S.args:
            if isinstance(part, sp.FiniteSet):
                out += list(part)
            elif isinstance(part, sp.ImageSet) and isinstance(interval, sp.Interval):
                out += _enumerate_linear_imageset(part, interval)
        return [sp.simplify(v) for v in out]

    return []
