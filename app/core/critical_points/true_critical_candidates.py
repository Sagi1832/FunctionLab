from typing import List, Optional, Tuple
import sympy as sp

from ..derivative import DerivativeEngine
from .critical_points import solve_raw_roots, keep_real

def dedupe_and_sort(roots: List[sp.Expr], tol: float = 1e-10) -> List[sp.Expr]:
    """ Return ascending list without numeric near-duplicates (|Δ|<=tol). """
    pairs: List[Tuple[float, sp.Expr]] = []
    for r in roots:
        try:
            v = float(sp.N(r))
        except Exception:
            v = float("inf")
        pairs.append((v, r))

    pairs.sort(key=lambda t: (t[0], sp.default_sort_key(t[1])))

    out: List[sp.Expr] = []
    last_val: Optional[float] = None
    for v, expr in pairs:
        if last_val is None or abs(v - last_val) > tol:
            out.append(sp.nsimplify(expr))
            last_val = v
    return out

def find_critical_candidates(
    engine: DerivativeEngine,
    interval: Optional[sp.Interval] = None,
    tol: float = 1e-10,
    ) -> List[sp.Expr]:
    """ Return real, deduped, sorted solutions of f'(x)=0 
    (restricted to interval if given). """
    x = engine.symbol
    fprime = engine.simplify_derivative()
    roots = solve_raw_roots(fprime, x, interval=interval, require_interval_if_infinite=True)
    roots = keep_real(roots, tol)
    roots = dedupe_and_sort(roots, tol)
    return roots


def find_critical_candidates_simple(
    f: sp.Expr,
    x: sp.Symbol,
    *,
    fprime: Optional[sp.Expr] = None,
    interval: Optional[sp.Interval] = None,
    require_interval_if_infinite: bool = True,
    tol: float = 1e-10,
) -> List[sp.Expr]:
    """ Returns real, deduped, sorted solutions of f'(x)=0. """
    if fprime is None:
        fprime = sp.diff(sp.simplify(f), x)

    roots = solve_raw_roots(
        fprime, x,
        interval=interval,
        require_interval_if_infinite=require_interval_if_infinite,
    )
    roots = keep_real(roots, tol)
    roots = dedupe_and_sort(roots, tol)
    return roots



