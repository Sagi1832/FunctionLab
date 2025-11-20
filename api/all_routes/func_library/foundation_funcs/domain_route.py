# TODO: Engine errors are mapped to HTTP 400 via EngineCallError
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from api.kafka.engine_calls.domain import call_domain
from api.kafka.client import EngineCallError

router = APIRouter()

class DomainIn(BaseModel):
    expr: str
    var: str = "x"
    
class DomainOut(BaseModel):
    raw: str


@router.post("/domain", response_model=DomainOut)
async def domain(body: DomainIn) -> DomainOut:
    try:
        data = await call_domain(expr=body.expr, var=body.var)
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
    
    return DomainOut(raw=data.get("raw", ""))
