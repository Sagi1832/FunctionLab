from pydantic import BaseModel


class AnalyzeIn(BaseModel):
    """Input model for function analysis API endpoints."""
    
    expression: str
    symbol: str = "x"
    interval: str | None = None  # string like "(-oo, oo)" or "[0, 5]"
    taylor_point: float | None = None
    taylor_order: int | None = None
