# TODO: Engine errors are mapped to HTTP 400 via EngineCallError
from typing import Dict, List, Tuple
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from api.kafka.engine_calls.extrema_and_monotonic import call_extrema_and_monotonic
from api.kafka.client import EngineCallError

router = APIRouter()
class ExtremaMonoIn(BaseModel):
    expr: str
    var: str = "x"
    interval: Tuple[float, float] = Field(description="Required interval [a,b] (numbers only)")
    closed: Tuple[bool, bool] = (True, True) 

class ExtremumOut(BaseModel):
    point: str  
    label: str  

class ExtremaMonoOut(BaseModel):
    monotonic: Dict[str, str]      
    extrema: List[ExtremumOut]

@router.post("/extrema_and_monotonic", response_model=ExtremaMonoOut)
async def extrema_and_monotonic_endpoint(body: ExtremaMonoIn) -> ExtremaMonoOut:
    try:
        data = await call_extrema_and_monotonic(
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
    
    monotonic = data.get("monotonic", {})
    extrema_data = data.get("extrema", [])
    extrema_out = [
        ExtremumOut(point=e.get("point", ""), label=e.get("label", ""))
        for e in extrema_data
    ]
    return ExtremaMonoOut(monotonic=monotonic, extrema=extrema_out)
