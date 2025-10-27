from typing import Iterable, Tuple, Union
import sympy as sp

from .domain import compute_domain as function_domain

IntervalLike = Union[sp.Interval, Tuple[float, float], Iterable[float]]

def _to_interval(interval: IntervalLike) -> sp.Interval:
    """ creates an interval """
    if isinstance(interval, sp.Interval):
        return interval
    try:
        a, b = list(interval)
    except Exception:
        raise ValueError("interval must be an sp.Interval or an iterable of two numbers (a, b).")
    try:
        iv = sp.Interval(a, b)
    except Exception:
        raise ValueError("failed to construct Interval; endpoints must be numeric")
    return iv

def require_interval_minimal(expr: sp.Expr, var: sp.Symbol, interval: IntervalLike) -> sp.Interval:
    """ validates the interval """
    iv = _to_interval(interval)
    a, b = iv.start, iv.end

    if not (a.is_real and b.is_real and a.is_finite and b.is_finite):
        raise ValueError("interval endpoints must be real and finite")

    if getattr(iv, "measure", 0) <= 0:
        raise ValueError("interval must have positive measure (ensure a < b).")

    dom = function_domain(expr, var)
    inter = iv.intersect(dom)

    if inter is sp.EmptySet or getattr(inter, "measure", 0) == 0:
        raise ValueError("interval must overlap the domain with positive measure.")
    return iv

def prompt_interval_until_valid(expr: sp.Expr, var: sp.Symbol) -> sp.Interval:
    """ asks for a valid interval again if the last one wasn't """
    while True:  
        raw = input("Enter interval as a,b (e.g. -2, 5): ").strip()

        if raw and raw[0] in "([{":
            raw = raw[1:]
        if raw and raw[-1] in ")]}":
            raw = raw[:-1]

        try:
            a_str, b_str = raw.split(",", 1)
            a, b = float(a_str.strip()), float(b_str.strip())
            return require_interval_minimal(expr, var, (a, b))
        except ValueError as e:
            print(f"Invalid interval: {e}")
        except Exception:
            print("Invalid format. Please type two numbers separated by a comma, e.g. -2, 5.")


validate_interval = require_interval_minimal