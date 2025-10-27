from __future__ import annotations
from typing import List
import sympy as sp
from .numeric import as_float

def candidate_open_intervals(edges: List[sp.Expr], *, tol: float) -> List[sp.Interval]:
    out: List[sp.Interval] = []
    for a, b in zip(edges, edges[1:]):
        try:
            af, bf = as_float(a), as_float(b)
            if abs(bf - af) <= tol:
                continue
        except Exception:
            pass
        try:
            iv = sp.Interval.open(a, b)
            if getattr(iv, "measure", 0) > 0:
                out.append(iv)
        except Exception:
            continue
    return out
