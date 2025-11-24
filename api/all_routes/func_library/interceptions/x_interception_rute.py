# TODO: Engine errors are mapped to HTTP 400 via EngineCallError
from typing import List, Optional, Tuple
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from api.kafka.engine_calls.x_intercepts import call_x_intercepts
from api.kafka.client import EngineCallError

router = APIRouter()
class XInterceptionIn(BaseModel):
    expr: str
    var: str = "x"
    interval: Optional[Tuple[float, float]] = Field(
        default=None, description="Optional interval [a,b] as two numbers"
    )
    closed: Optional[Tuple[bool, bool]] = (True, True)


class XInterceptionOut(BaseModel):
    points: List[str]


@router.post("/x_intercepts", response_model=XInterceptionOut)
async def x_intercepts_endpoint(body: XInterceptionIn) -> XInterceptionOut:
    try:
        data = await call_x_intercepts(
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
    
    points = data.get("points", [])
    return XInterceptionOut(points=points)
