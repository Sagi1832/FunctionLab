from __future__ import annotations
from typing import List, Tuple, Optional
import math
import sympy as sp

def as_float(x: sp.Expr) -> float:
    if x is sp.S.NegativeInfinity: 
        return -math.inf
    if x is sp.S.Infinity:         
        return math.inf
    try:
        return float(sp.N(x))
    except Exception:
        return float(sp.N(sp.nsimplify(x)))

def dedupe_sorted(vals: List[sp.Expr], tol: float) -> List[sp.Expr]:
    pairs: List[Tuple[float, sp.Expr]] = []
    for v in vals:
        try: 
            pairs.append((as_float(v), v))
        except Exception: 
            pairs.append((math.inf, v))
    pairs.sort(key=lambda t: (t[0], sp.default_sort_key(t[1])))
    out: List[sp.Expr] = []
    last: Optional[float] = None
    for f, expr in pairs:
        if (last is None) or (math.isinf(f) and f != last) or (abs(f-last) > tol):
            out.append(sp.nsimplify(expr))
            last = f
    return out

def eval_derivative_sign(fprime: sp.Expr, var: sp.Symbol, t: float) -> Optional[str]:
    try:
        val = sp.N(fprime.subs(var, t))
        if getattr(val, "is_real", None) is not True:
            val = complex(val) 
            val = val.real if abs(val.imag) <= 1e-9 else val
        v = float(val)
        if abs(v) < 1e-9:
            for eps in (1e-6, -1e-6, 1e-4, -1e-4):
                vv = float(sp.N(fprime.subs(var, t+eps)))
                if abs(vv) >= 1e-9: 
                    v = vv 
                break
        return "inc" if v > 0 else "dec"
    except Exception:
        for eps in (1e-3, -1e-3, 1e-2, -1e-2, 1e-1, -1e-1):
            try:
                vv = float(sp.N(fprime.subs(var, t+eps)))
                if abs(vv) >= 1e-9: 
                    return "inc" if vv > 0 else "dec"
            except Exception:
                pass
    return None
