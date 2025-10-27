# NOTE: Glue-only module. No business logic here.
from __future__ import annotations
from typing import List, Optional, Tuple, Dict
import sympy as sp

from app.core.foundation import compute_domain

from .x_asymptotes_check import (
    x_candidates_from_domain,
    domain_boundary_points_simple_from_domain,
    final_x_asymptote,
)

from .asymptotes_and_holes_filter import (
    detect_holes_via_limits,
    filter_x_asymptotes,
    keep_true_vertical_asymptotes,
)

from .y_asymptotes_check import horizontal_asymptotes as _horizontal_asymptotes


def asymptotes_summary(
    f: sp.Expr, x: sp.Symbol, interval: Optional[sp.Interval] = None
) -> Dict[str, object]:
    """ Returns a dictionary with the vertical, horizontal, and holes asymptotes. """
    return {
        "vertical": find_vertical_asymptotes(f, x, interval=interval),
        "horizontal": find_horizontal_asymptotes(f, x),
        "holes": find_holes(f, x, interval=interval),
    }

def find_vertical_asymptotes(
    f: sp.Expr, x: sp.Symbol, interval: Optional[sp.Interval] = None
) -> List[sp.Expr]:
    """ Returns a list of vertical asymptotes of the function f(x) on the given interval. """
    dom = compute_domain(f, x)

    raw = x_candidates_from_domain(dom, interval=interval, f=f, x=x)

    holes = detect_holes_via_limits(f, x, raw, interval=interval)
    cand  = filter_x_asymptotes(raw, holes)

    vas = keep_true_vertical_asymptotes(f, x, cand, interval=interval)

    return final_x_asymptote(vas)


x_asymptotes = find_vertical_asymptotes


def find_horizontal_asymptotes(
    f: sp.Expr, x: sp.Symbol
) -> Dict[str, Optional[sp.Expr]]:
    """ Returns a dictionary with the horizontal asymptotes of the function f(x). """
    return _horizontal_asymptotes(f, x)


def find_holes(
    f: sp.Expr, x: sp.Symbol, interval: Optional[sp.Interval] = None
) -> List[Tuple[sp.Expr, sp.Expr]]:
    """ Returns a list of holes in the function f(x) on the given interval. """
    dom = compute_domain(f, x)
    raw = domain_boundary_points_simple_from_domain(dom, interval=interval)
    return detect_holes_via_limits(f, x, raw, interval=interval)



__all__ = [
    "find_vertical_asymptotes",
    "find_horizontal_asymptotes",
    "find_holes",
    "asymptotes_summary",
    "x_asymptotes",
]
