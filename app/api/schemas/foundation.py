# app/api/schemas/foundation.py
from pydantic import BaseModel
from typing import List, Optional

class IntervalDTO(BaseModel):
    a: Optional[float] = None
    b: Optional[float] = None
    left_open: bool
    right_open: bool

class DomainRequest(BaseModel):
    expr: str
    var: str = "x"

class DomainResponse(BaseModel):
    intervals: List[IntervalDTO]
    excluded_points: List[float]
    raw: str
    ok: bool
