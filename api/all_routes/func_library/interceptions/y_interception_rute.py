# TODO: Engine errors are mapped to HTTP 400 via EngineCallError
from typing import Optional, Tuple
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from api.kafka.engine_calls.y_intercept import call_y_intercept
from api.kafka.client import EngineCallError

router = APIRouter()
class YInterceptionIn(BaseModel):
    expr: str
    var: str = "x"
    interval: Optional[Tuple[float, float]] = Field(
        default=None, description="Optional interval [a,b] as two numbers"
    )
    closed: Optional[Tuple[bool, bool]] = (True, True)

class YInterceptionOut(BaseModel):
    point: Optional[str] = None

@router.post("/y_intercepts", response_model=YInterceptionOut)
async def y_intercepts_endpoint(body: YInterceptionIn) -> YInterceptionOut:
    try:
        data = await call_y_intercept(
            expr=body.expr,
            var=body.var,
            interval=body.interval,
            closed=body.closed
        )
    except EngineCallError as e:
        # engine answered with ok=False
        raise HTTPException(
            status_code=400,
            detail=f"engine error: {e}",
        )
    except HTTPException:
        # re-raise any HTTPException we already raised
        raise
    except Exception as e:
        # bad user input / unexpected error
        raise HTTPException(
            status_code=400,
            detail=f"invalid input: {e}",
        )
    
    point = data.get("point")
    return YInterceptionOut(point=point)
