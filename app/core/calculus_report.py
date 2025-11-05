from typing import List, Tuple, Dict, Any, Optional
import sympy as sp
from dataclasses import dataclass, field


@dataclass
class CalculusReport:
    raw_input: Optional[str] = None
    symbol: sp.Symbol = field(default_factory=lambda: sp.Symbol("x"))

    expr: Optional[sp.Expr] = None
    domain: Optional[sp.Set] = None
    derivative: Optional[sp.Expr] = None

    # critical points
    critical_points: List[float] = field(default_factory=list)
    extrema: Dict[str, List[Tuple[float, float]]] = field(
        default_factory=lambda: {"mins": [], "maxs": []}
    )
    monotonicity: List[Tuple[str, sp.Interval]] = field(default_factory=list)  # ("increasing"/"decreasing", Interval)
    intercepts: Dict[str, List[Tuple[float, float]]] = field(
        default_factory=lambda: {"x": [], "y": []}
    )

    # taylor
    taylor: Dict[str, Any] = field(
        default_factory=lambda: {"point": 0.0, "order": 3, "series": None}
    )

    # asymptotes
    asymptotes: Dict[str, List[sp.Eq]] = field(
        default_factory=lambda: {"vertical": [], "horizontal": [], "oblique": []}
    )

    # exeptions 
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
