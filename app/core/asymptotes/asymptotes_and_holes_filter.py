from __future__ import annotations
from typing import List, Optional, Tuple
import sympy as sp

from app.core.foundation.limits import limit_at_point

    



def detect_holes_via_limits(
    f: sp.Expr,
    x: sp.Symbol,
    candidates: List[sp.Expr],
    interval: Optional[sp.Interval] = None,
    ) -> List[Tuple[sp.Expr, sp.Expr]]:
    """Check each undefined point; if two-sided finite limit exists -> hole (x0, y0)."""
    holes: List[Tuple[sp.Expr, sp.Expr]] = []

    for c in candidates:
        # skip endpoints: אין שני צדדים אמיתיים בקצה האינטרוול
        if isinstance(interval, sp.Interval) and (sp.Eq(c, interval.start) or sp.Eq(c, interval.end)):
            continue

        Lm = limit_at_point(f, x, c, side='-')
        Lp = limit_at_point(f, x, c, side='+')

        if Lm is None or Lp is None:
            continue
        if Lm in (sp.oo, -sp.oo, sp.zoo) or Lp in (sp.oo, -sp.oo, sp.zoo):
            continue

        try:
            same = bool(sp.simplify(Lm - Lp) == 0)
        except Exception:
            same = False

        if same:
            holes.append((sp.simplify(c), sp.simplify(Lm)))

    return holes


def filter_x_asymptotes(raw_x: List[sp.Expr], holes: List[Tuple[sp.Expr, sp.Expr]]) -> List[sp.Expr]:
    """(אופציונלי) Keep only x=c that are not holes."""
    hole_xs = [hx for (hx, _) in holes]
    out: List[sp.Expr] = []
    for c in raw_x:
        if all(sp.simplify(c - hx) != 0 for hx in hole_xs):
            out.append(sp.simplify(c))
    return out


def keep_true_vertical_asymptotes(
    f: sp.Expr,
    x: sp.Symbol,
    candidates_without_holes: List[sp.Expr],
    interval: Optional[sp.Interval] = None,
) -> List[sp.Expr]:
    """Keep only x=c where at least one one-sided limit is ±oo (order-preserving)."""
    out: List[sp.Expr] = []

    for c in candidates_without_holes:
        sides = ['-', '+']
        if isinstance(interval, sp.Interval):
            if sp.Eq(c, interval.start):
                sides = ['+']
            elif sp.Eq(c, interval.end):
                sides = ['-']

        for side in sides:
            try:
                L = sp.limit(f, x, c, dir=side)
            except Exception:
                L = None
            if L in (sp.oo, -sp.oo, sp.zoo):
                out.append(sp.simplify(c))
                break

    # dedup while preserving order
    uniq: List[sp.Expr] = []
    for c in out:
        if not any(sp.simplify(c - u) == 0 for u in uniq):
            uniq.append(c)
    return uniq
