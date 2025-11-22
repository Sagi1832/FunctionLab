from typing import Tuple, Dict
import sympy as sp
from app.utils.adapters import sympy_locals, sstr_ln
from app.core.monotonic.monotonicity import monotonicity_intervals

def _mk_interval(iv: Tuple[float, float], closed: Tuple[bool, bool]) -> sp.Interval:
    """Create a sympy interval from a tuple of floats and a tuple of bools."""
    a, b = float(iv[0]), float(iv[1])
    if not (a < b):
        raise ValueError("interval must satisfy a < b.")
    lc, rc = closed
    return sp.Interval(a, b, left_open=not lc, right_open=not rc)

def _interval_to_str(iv: sp.Interval) -> str:
    """Return the interval string for iv."""
    lb = "(" if iv.left_open else "["
    rb = ")" if iv.right_open else "]"
    return f"{lb}{sstr_ln(iv.start)}, {sstr_ln(iv.end)}{rb}"

def _point_to_str(x0: sp.Expr, y0: sp.Expr) -> str:
    """Return the point string for (x0, y0)."""
    return f"({sstr_ln(x0)}, {sstr_ln(y0)})"

def _monotonic_output(eng, iv) -> Dict[str, str]:
    """Return a dictionary of intervals and their monotonicity ('inc'/'dec')."""
    mono = monotonicity_intervals(eng, interval=iv)
    return {_interval_to_str(seg): str(sign) for (seg, sign) in mono}


def interval_str_clipped(seg: sp.Interval, iv: sp.Interval) -> str:
    """Return the interval string for (seg ∩ iv)."""
    clipped = seg.intersect(iv)
    if clipped.is_EmptySet:
        return ""
    return _interval_to_str(clipped)

