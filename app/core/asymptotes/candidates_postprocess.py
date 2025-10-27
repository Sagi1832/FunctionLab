from __future__ import annotations
from typing import List, Optional, Tuple
import sympy as sp


def restrict_candidates_to_interval(
    candidates: List[sp.Expr],
    interval: Optional[sp.Interval],
    ) -> List[sp.Expr]:
    """Keep only candidates that lie inside the given interval (respecting open/closed ends)."""
    if not isinstance(interval, sp.Interval):
        out: List[sp.Expr] = []
        for c in candidates:
            c_s = sp.simplify(c)
            if not any(sp.simplify(c_s - u) == 0 for u in out):
                out.append(c_s)
        return out

    out: List[sp.Expr] = []
    a, b = interval.start, interval.end

    for c in candidates:
        c_s = sp.simplify(c)

        on_left  = (not interval.left_open)  and (sp.simplify(c_s - a) == 0)
        on_right = (not interval.right_open) and (sp.simplify(c_s - b) == 0)
        if on_left or on_right:
            if not any(sp.simplify(c_s - u) == 0 for u in out):
                out.append(c_s)
            continue

        try:
            inside = bool(interval.contains(c_s))
        except Exception:
            try:
                inside = bool((c_s > a) & (c_s < b))
            except Exception:
                inside = False

        if inside and all(sp.simplify(c_s - u) != 0 for u in out):
            out.append(c_s)

    return out


def remove_holes_from_candidates(
    candidates: List[sp.Expr],
    holes: List[Tuple[sp.Expr, sp.Expr]],
    ) -> List[sp.Expr]:
    """Remove x-values that are holes from the candidates list (order-preserving)."""
    hole_xs = [sp.simplify(hx) for (hx, _) in holes]
    out: List[sp.Expr] = []
    for c in candidates:
        c_s = sp.simplify(c)
        if all(sp.simplify(c_s - hx) != 0 for hx in hole_xs):
            if all(sp.simplify(c_s - u) != 0 for u in out):
                out.append(c_s)
    return out
