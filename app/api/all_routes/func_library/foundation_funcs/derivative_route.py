import sympy as sp
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.core.foundation.derivative import DerivativeEngine
from app.api.adapters import sympy_locals
from app.api.adapters import sstr_ln

router = APIRouter()

class DerivativeIn(BaseModel):
    expr: str
    var: str = "x"

class DerivativeOut(BaseModel):
    raw: str  


@router.post("/derivative", response_model=DerivativeOut)
def derivative_endpoint(body: DerivativeIn) -> DerivativeOut:
    try:
        x = sp.Symbol(body.var, real=True)
        expr = sp.sympify(body.expr, locals=sympy_locals(body.var, x))
        eng = DerivativeEngine(expr, x)
        d = eng.simplify_derivative()

        return DerivativeOut(raw=sstr_ln(d))

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"invalid input: {e}")
