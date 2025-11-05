from typing import Tuple, Dict
import sympy as sp
from app.api.adapters import sympy_locals, sstr_ln
from app.core.monotonic.monotonicity import monotonicity_intervals

def _mk_interval(iv: Tuple[float, float], closed: Tuple[bool, bool]) -> sp.Interval:
    a, b = float(iv[0]), float(iv[1])
    if not (a < b):
        raise ValueError("interval must satisfy a < b.")
    lc, rc = closed
    return sp.Interval(a, b, left_open=not lc, right_open=not rc)

def _interval_to_str(iv: sp.Interval) -> str:
    lb = "(" if iv.left_open else "["
    rb = ")" if iv.right_open else "]"
    return f"{lb}{sstr_ln(iv.start)}, {sstr_ln(iv.end)}{rb}"

def _point_to_str(x0: sp.Expr, y0: sp.Expr) -> str:
    return f"({sstr_ln(x0)}, {sstr_ln(y0)})"

def _monotonic_output(eng, iv) -> Dict[str, str]:
    mono = monotonicity_intervals(eng, interval=iv)
    return {_interval_to_str(seg): str(sign) for (seg, sign) in mono}


def interval_str_clipped(seg: sp.Interval, iv: sp.Interval) -> str:
    """Return the interval string for (seg ∩ iv)."""
    clipped = seg.intersect(iv)
    if clipped.is_EmptySet:
        return ""
    return _interval_to_str(clipped)