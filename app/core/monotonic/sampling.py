from __future__ import annotations
import math
import sympy as sp
from .numeric import as_float

def midpoint(a: sp.Expr, b: sp.Expr) -> float:
    af, bf = as_float(a), as_float(b)
    if math.isfinite(af) and math.isfinite(bf): 
        return (af+bf)/2.0
    if not math.isfinite(af) and math.isfinite(bf): 
        return bf - 1.0
    if math.isfinite(af) and not math.isfinite(bf): 
        return af + 1.0
    return 0.0
