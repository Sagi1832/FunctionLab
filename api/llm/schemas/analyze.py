from __future__ import annotations

from enum import Enum
from typing import Optional, Tuple

from pydantic import BaseModel


class Action(str, Enum):
    """The action to perform."""
    domain = "domain"
    derivative = "derivative"
    x_intercepts = "x_intercepts"
    y_intercepts = "y_intercepts"
    asymptotes_and_holes = "asymptotes_and_holes"
    extrema_and_monotonic = "extrema_and_monotonic"


class AnalyzeRequest(BaseModel):
    """Structured request for /llm/analyze."""
    raw: str
    var: str = "x"
    action: Action
    interval: Optional[Tuple[float, float]] = None
    closed: Optional[Tuple[bool, bool]] = None
    present: bool = True
    narrate: bool = False
    narrate_lang: str = "en"


class AnalyzeResponse(BaseModel):
    """Response returned from the engine + presenter pipeline."""
    action: str
    expr: str
    var: str
    present: str
    warnings: list[str] = []
    errors: list[str] = []
