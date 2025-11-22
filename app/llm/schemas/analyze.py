from __future__ import annotations
from enum import Enum
from typing import Optional, Tuple, Dict, Any, List
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
    """The request to analyze."""
    raw: str
    var: str = "x"
    action: Action
    interval: Optional[Tuple[float, float]] = None
    closed: Optional[Tuple[bool, bool]] = None
    present: bool = True
    narrate: bool = False  
    narrate_lang: str = "en"  

class AnalyzeResult(BaseModel):
    """The result of the analysis."""
    action: Action
    expr: str
    var: str
    report: Dict[str, Any]
    warnings: List[str] = []
    errors: List[str] = []

class AnalyzeResponse(BaseModel):
    """The response from /llm/analyze endpoint.
    
    This is the external schema sent via Kafka to the API.
    It contains only the final human-friendly explanation, not the raw CalculusReport.
    """
    action: Action
    expr: str
    var: str
    present: str  # Required: final human-friendly explanation from presenter LLM
    warnings: List[str] = []
    errors: List[str] = []