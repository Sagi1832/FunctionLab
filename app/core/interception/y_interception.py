from typing import Optional
import sympy as sp
from app.core.foundation import compute_domain  # או from app.core.domain import compute_domain


def y_intercept(
    f: sp.Expr,
    x: sp.Symbol,
    interval: Optional[sp.Interval] = None,
) -> Optional[sp.Expr]:
    """ Return the y intercept (value of f(0)) if it exists, otherwise None. """
    dom = compute_domain(f, x)
    eff_dom = dom.intersect(interval) if isinstance(interval, sp.Interval) else dom

    c = eff_dom.contains(0)
    if not (c is True or c is sp.S.true):
        return None

    try:
        y0 = sp.simplify(f.subs(x, 0))
    except Exception:
        return None

    if not _finite_scalar(y0):
        return None

    return sp.nsimplify(y0)


def _finite_scalar(v: sp.Expr) -> bool:
    """ Check if the value v is a finite scalar. """
    if isinstance(v, sp.AccumBounds):
        return False
    return not (v.has(sp.nan) or v.has(sp.zoo) or v.has(sp.oo) or v.has(-sp.oo))


