from __future__ import annotations
from typing import Iterable, List, Optional
import sympy as sp
from .numeric import dedupe_sorted
from ..critical_points import find_critical_candidates_simple
from .sets import collect_boundaries

def build_cut_points(
    work_set: sp.Set,
    iv: Optional[sp.Interval],
    *,
    f: sp.Expr,
    x: sp.Symbol,
    fprime: Optional[sp.Expr],
    critical_points: Optional[Iterable[sp.Expr]],
    singulars: Optional[Iterable[sp.Expr]],
    tol: float,
) -> List[sp.Expr]:
    cuts: List[sp.Expr] = []
    cuts.extend(collect_boundaries(work_set))
    if iv is not None:
        cuts.extend([iv.start, iv.end])

    if critical_points is None:
        fp = fprime if fprime is not None else sp.diff(sp.simplify(f), x)
        cuts.extend(find_critical_candidates_simple(f, x, fprime=fp, interval=iv, tol=tol))
    else:
        cuts.extend(list(critical_points))

    if singulars is not None:
        cuts.extend(list(singulars))

    return dedupe_sorted(cuts, tol=tol)
