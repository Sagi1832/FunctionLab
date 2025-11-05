from __future__ import annotations
from typing import Any, Dict, Tuple, Optional

class APIMethodsMixin:
    """High-level API methods that call the backend endpoints via self._post()."""
    def domain(self, *, expr: str, var: str) -> Dict[str, Any]:
        """Find the domain of a function."""
        return self._post("/domain", {"expr": expr, "var": var})

    def derivative(self, *, expr: str, var: str) -> Dict[str, Any]:
        """Find the derivative of a function."""
        return self._post("/derivative", {"expr": expr, "var": var})

    # ---- intercepts ----
    def x_intercepts(self, *, expr: str, var: str) -> Dict[str, Any]:
        """Find x-intercepts."""
        return self._post("/x_intercepts", {"expr": expr, "var": var})

    def y_intercepts(self, *, expr: str, var: str) -> Dict[str, Any]:
        """Find y-intercepts."""
        return self._post("/y_intercepts", {"expr": expr, "var": var})

    def intercepts(self, *, expr: str, var: str) -> Dict[str, Any]:
        """Return both x and y intercepts in a single response (if יש כזה ראוט)."""
        xrep = self.x_intercepts(expr=expr, var=var)
        yrep = self.y_intercepts(expr=expr, var=var)
        return {"x_intercepts": xrep, "y_intercepts": yrep}

    # ---- asymptotes & holes ----
    def asymptotes_and_holes(self, *, expr: str, var: str) -> Dict[str, Any]:
        """Find asymptotes and holes."""
        return self._post("/asymptotes_and_holes", {"expr": expr, "var": var})

    # ---- limits ----
    def limits(self, *, expr: str, var: str) -> Dict[str, Any]:
        """Find relevant limits (לפי איך שהראוט שלך מיישם)."""
        return self._post("/limits", {"expr": expr, "var": var})

    # ---- extrema & monotonic ----
    def extrema_and_monotonic(self, *, expr: str, var: str, interval: Optional[Tuple[float, float]] = None, closed: Optional[Tuple[bool, bool]] = None) -> Dict[str, Any]:
        payload = {"expr": str(expr), "var": var}
        if interval is not None:
            payload["interval"] = list(interval)
        if closed is not None:
            payload["closed"] = list(closed)
        return self._post("/extrema_and_monotonic", json=payload)
