import sympy as sp
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.core.foundation.validation import needs_interval
from app.api.adapters import sympy_locals

router = APIRouter()

class NeedIntervalIn(BaseModel):
    expr: str
    var: str = "x"
    

class NeedIntervalOut(BaseModel):
    answer: bool

@router.post("/need_interval", response_model=NeedIntervalOut)
def need_interval(body: NeedIntervalIn):
    try:
        x = sp.Symbol(body.var, real=True)
        f = sp.sympify(body.expr, locals=sympy_locals(body.var, x))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"invalid input: {e}")
    return NeedIntervalOut(answer=needs_interval(f, x))
