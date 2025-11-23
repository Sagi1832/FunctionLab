from __future__ import annotations
from typing import Dict, List, Optional, Tuple
import sympy as sp

from ..foundation.derivative import DerivativeEngine
from ..critical_points.true_critical_candidates import find_critical_candidates

from .numeric import as_float, dedupe_sorted, eval_derivative_sign
from .keys import interval_key, parse_key
from .sampling import midpoint
from .sets import ensure_work_set, collect_boundaries, contains_real


def monotonicity_map(
    engine: DerivativeEngine,
    interval: Optional[sp.Interval] = None,
    *,
    tol: float = 1e-10,
) -> Dict[str, str]:
    """ Returns a dictionary of intervals and their monotonicity ('inc'/'dec'). """
    x = engine.symbol
    fprime = engine.simplify_derivative()

    sp_simpl = sp.simplify(fprime)
    if getattr(sp_simpl, "is_zero", None) is True or sp.simplify(fprime == 0):
        return {}

    work_set, iv = ensure_work_set(engine.expr, x, interval)
    edges = _candidate_edges(work_set=work_set, iv=iv, engine=engine, tol=tol)

    result: Dict[str, str] = {}
    for a, b in zip(edges, edges[1:]):
        if _is_trivial_span(a, b, tol=tol):
            continue

        t = _pick_sample_in_span(work_set, a, b)
        if t is None:
            continue 

        sign = _label_span(fprime, x, t)
        if sign is None:
            continue

        result[interval_key(a, b)] = sign

    return result

def monotonicity_intervals(
    engine: DerivativeEngine,
    interval: Optional[sp.Interval] = None,
    *,
    tol: float = 1e-10,
) -> List[Tuple[sp.Interval, str]]:
    """ Returns a list of intervals and their monotonicity ('inc'/'dec'). """
    m = monotonicity_map(engine, interval=interval, tol=tol)
    return [(parse_key(k), v) for k, v in m.items()]


def _is_trivial_span(a: sp.Expr, b: sp.Expr, *, tol: float) -> bool:
    """ Whether the span (a,b) is too small numerically. """
    try:
        return abs(as_float(b) - as_float(a)) <= tol
    except Exception:
        return False


def _candidate_edges(
    *,
    work_set: sp.Set,
    iv: Optional[sp.Interval],
    engine: DerivativeEngine,
    tol: float,
) -> List[sp.Expr]:
    """ Builds a list of intersection points (domain boundaries, critical points, boundaries). """
    cuts: List[sp.Expr] = []
    cuts.extend(collect_boundaries(work_set))
    if iv is not None:
        cuts.extend([iv.start, iv.end])

    cuts.extend(find_critical_candidates(engine, interval=iv, tol=tol))

    cuts = dedupe_sorted(cuts, tol=tol)

    return [sp.S.NegativeInfinity] + cuts + [sp.S.Infinity]


def _pick_sample_in_span(
    work_set: sp.Set, a: sp.Expr, b: sp.Expr
) -> Optional[float]:
    """ Picks a sample in the span (a,b) that is in the work_set. """
    t = midpoint(a, b)
    if contains_real(work_set, t):
        return t

    bumps = (1e-3, 1e-2, 1e-1, 1.0)
    left_is_inf = (a is sp.S.NegativeInfinity)
    for eps in bumps:
        cand = t + (eps if left_is_inf else -eps)
        if contains_real(work_set, cand):
            return cand
    return None


def _label_span(
    fprime: sp.Expr, x: sp.Symbol, t: float
) -> Optional[str]:
    """ Returns 'inc'/'dec' based on the sign of the derivative at t, or None if not determinable. """
    return eval_derivative_sign(fprime, x, t)





