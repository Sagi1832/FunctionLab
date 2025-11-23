"""
Package-level file for app.core.

This module exists only for type-checking convenience. Runtime code should import
directly from subpackages like:
- app.core.foundation (DerivativeEngine, compute_domain, etc.)
- app.core.critical_points (find_critical_candidates, classify_extrema_from_monotonic)
- app.core.monotonic (monotonicity_intervals, monotonicity_map)
- app.core.asymptotes (asymptotes_summary, etc.)
- app.core.interception (x_intercepts, y_intercept)
"""
from __future__ import annotations
from typing import TYPE_CHECKING

__all__: list[str] = []

# Type hints only - not used at runtime
if TYPE_CHECKING:
    from .foundation import (
        DerivativeEngine,
        compute_domain,
        require_interval_minimal,
        validate_interval,
        limit_at_point,
        needs_interval,
    )
    from .critical_points.extreme_points import (
        classify_extrema_from_monotonic,
        find_extreme_points,
    )
