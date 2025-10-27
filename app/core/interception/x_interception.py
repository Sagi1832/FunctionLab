from typing import List, Optional
import sympy as sp
from app.core.foundation import compute_domain  # או from app.core.domain import compute_domain

def x_intercepts(
    f: sp.Expr,
    x: sp.Symbol,
    interval: Optional[sp.Interval] = None,
) -> List[sp.Expr]:
    """ Return x intercepts of the function f(x) on the given interval. """
    dom = compute_domain(f, x)
    eff_dom = dom.intersect(interval) if isinstance(interval, sp.Interval) else dom

    solset = sp.solveset(sp.Eq(f, 0), x, domain=eff_dom)
    if not isinstance(solset, sp.FiniteSet):
        return []

    out: List[sp.Expr] = []
    for s in list(solset):
        s_s = sp.simplify(s)
        if not _contains(eff_dom, s_s):
            continue
        # ודא שהערך סופי ונותן y=0 באמת
        if not _is_finite_value(f, x, s_s):
            continue
        out.append(sp.nsimplify(s_s))
    return out


def _contains(s: sp.Set, v: sp.Expr) -> bool:
    """ Check if the value v is in the set s. """
    c = s.contains(v)
    if c is True or c is sp.S.true:
        return True
    if c is False or c is sp.S.false:
        return False
    return False


def _is_finite_value(f: sp.Expr, x: sp.Symbol, a: sp.Expr) -> bool:
    """ Check if the value a is a finite value of the function f(x) at the point x. """
    try:
        val = sp.simplify(f.subs(x, a))
    except Exception:
        return False
    if isinstance(val, sp.AccumBounds):
        return False
    if val.has(sp.nan) or val.has(sp.zoo) or val.has(sp.oo) or val.has(-sp.oo):
        return False
    return True




