from __future__ import annotations
from typing import Any, Dict, Optional, List
import sympy as sp

from .asymptotes.x_asymptotes_check import (
    domain_boundary_points_simple_from_domain as x_candidates_from_domain
)

from .asymptotes.y_asymptotes_check import horizontal_asymptotes

from .asymptotes.asymptotes_and_holes_filter import (
    detect_holes_via_limits,
    keep_true_vertical_asymptotes,
)

from .asymptotes.candidates_postprocess import (
    restrict_candidates_to_interval,
    remove_holes_from_candidates,
)


def summarize_asymptotes(
    f: sp.Expr,
    x: sp.Symbol,
    domain: sp.Set,
    interval: Optional[sp.Interval] = None,
    ) -> Dict[str, Any]:
    cands: List[sp.Expr] = x_candidates_from_domain(domain, interval)

    cands = restrict_candidates_to_interval(cands, interval)

    holes = detect_holes_via_limits(f, x, cands, interval)

    cands_wo_holes = remove_holes_from_candidates(cands, holes)

    x_final = keep_true_vertical_asymptotes(f, x, cands_wo_holes, interval)

    y_final = horizontal_asymptotes(f, x)

    out: Dict[str, Any] = {"x": x_final, "y": y_final}
    if holes:
        out["holes"] = holes
    return out
