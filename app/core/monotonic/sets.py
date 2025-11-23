from __future__ import annotations
from typing import List, Optional
import sympy as sp
from ..foundation.domain import compute_domain
from ..foundation.interval_guard import require_interval_minimal

def ensure_work_set(expr: sp.Expr, var: sp.Symbol, interval: Optional[sp.Interval]):
    dom = compute_domain(expr, var)
    if interval is not None:
        iv = require_interval_minimal(expr, var, interval)
        return dom.intersect(iv), iv
    return dom, None

def collect_boundaries(S: sp.Set) -> List[sp.Expr]:
    out: List[sp.Expr] = []
    def rec(T: sp.Set):
        if isinstance(T, sp.Interval): 
            out.extend([T.start, T.end])
        elif isinstance(T, sp.Union):
            for part in T.args: 
                rec(part)
        elif isinstance(T, sp.Complement):
            base, removed = T.args
            rec(base)
            if isinstance(removed, sp.FiniteSet): 
                out.extend(list(removed))
        elif isinstance(T, sp.FiniteSet): 
            out.extend(list(T))
    rec(S)
    return out

def contains_real(S: sp.Set, x: float) -> bool:
    try: 
        return bool(sp.Contains(sp.Float(x), S))
    except Exception: 
        return True
