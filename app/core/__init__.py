from __future__ import annotations
from typing import TYPE_CHECKING

__all__: list[str] = []

# רק לרמזי טיפוסים בעורך; לא רץ בזמן אמת
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
