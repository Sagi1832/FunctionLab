from typing import List, Optional
import sympy as sp
from .x_asympototes_help import singular_candidates_in_interval


def domain_boundary_points_simple_from_domain(
    domain: sp.Set,
    interval: Optional[sp.Interval] = None,
) -> List[sp.Expr]:
    """Return all finite boundary points of the given real-domain set (optionally
    intersected with `interval`). Order-preserving, no numeric sorting, no temp
    'pieces' list.
    """
    D = domain if interval is None else sp.Intersection(domain, interval)
    U = sp.Union(D)
    pts: List[sp.Expr] = []

    iter_segs = (
        (U,) if isinstance(U, sp.Interval)
        else (p for p in U.args if isinstance(p, sp.Interval)) if isinstance(U, sp.Union)
        else ()
    )

    for seg in iter_segs:
        if seg.start not in (sp.oo, -sp.oo):
            pts.append(sp.simplify(seg.start))
        if seg.end not in (sp.oo, -sp.oo):
            pts.append(sp.simplify(seg.end))

    return final_x_asymptote(pts)


def x_candidates_from_domain(
    domain: sp.Set,
    interval: Optional[sp.Interval] = None,
    f: Optional[sp.Expr] = None,
    x: Optional[sp.Symbol] = None,
) -> List[sp.Expr]:
    """Return candidate x-values for vertical asymptotes.

    Always includes finite domain-boundary points (optionally intersected with `interval`).
    If `f` and `x` are provided, also includes singular candidates detected by
    `singular_candidates_in_interval(f, x, interval)` (e.g., tan poles).
    """
    pts = domain_boundary_points_simple_from_domain(domain, interval)

    if f is not None and x is not None:
        try:
            extras = singular_candidates_in_interval(f, x, interval)
            pts.extend(extras)
        except Exception:
            pass

    return final_x_asymptote(pts)



def final_x_asymptote(pts: List[sp.Expr]) -> List[sp.Expr]:
    """Deduplicate a list of x-candidates while preserving first appearance order.
    Equality is checked symbolically via simplify(c - u) == 0.
    """
    uniq: List[sp.Expr] = []
    for c in pts:
        c_s = sp.simplify(c)
        if not any(sp.simplify(c_s - u) == 0 for u in uniq):
            uniq.append(c_s)
    return uniq
