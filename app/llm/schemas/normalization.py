from __future__ import annotations
from pydantic import BaseModel, Field

class NormalizationRequest(BaseModel):
    """The request to normalize."""
    raw: str = Field(..., description="User free-text expression")
    var: str = Field("x", description="Primary variable")

class NormalizationResult(BaseModel):
    """The result of the normalization."""
    expr: str
    var: str = "x"
