# app/core/monotonicity.py (shim)
from warnings import warn
from .monotonic import monotonicity_intervals  # import למעלה -> שקט ללינטר

warn(
    "Import from 'app.core.monotonicity' is deprecated. Use 'app.core.monotonic' instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["monotonicity_intervals"]
