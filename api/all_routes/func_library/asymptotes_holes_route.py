# TODO: Engine errors are mapped to HTTP 400 via EngineCallError
from typing import Optional, Tuple, List, Dict
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException
from api.kafka.engine_calls.asymptotes_and_holes import call_asymptotes_and_holes
from api.kafka.client import EngineCallError

router = APIRouter()
class AsymptotesHolesIn(BaseModel):
    expr: str
    var: str = "x"
    interval: Optional[Tuple[float, float]] = Field(
        default=None, description="Optional interval [a,b] as two numbers"
    )
    closed: Optional[Tuple[bool, bool]] = (True, True)

class AsymptotesHolesOut(BaseModel):
    vertical: List[str] = []
    horizontal: Dict[str, Optional[str]] = {"left": None, "right": None}
    holes: List[str] = []    

@router.post("/asymptotes_and_holes", response_model=AsymptotesHolesOut)
async def asymptotes_and_holes_endpoint(body: AsymptotesHolesIn) -> AsymptotesHolesOut:
    try:
        data = await call_asymptotes_and_holes(
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
    
    return AsymptotesHolesOut(
        vertical=data.get("vertical", []),
        horizontal=data.get("horizontal", {"left": None, "right": None}),
        holes=data.get("holes", []),
    )



