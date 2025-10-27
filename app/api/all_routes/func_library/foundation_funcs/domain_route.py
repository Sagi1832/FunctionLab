import sympy as sp
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.core.foundation.domain import compute_domain
from app.api.adapters import sympy_locals

router = APIRouter()

class DomainIn(BaseModel):
    expr: str
    var: str = "x"
    
class DomainOut(BaseModel):
    raw: str


@router.post("/domain", response_model=DomainOut)
def domain(body: DomainIn) -> DomainOut:
    try:
        x = sp.Symbol(body.var, real=True)
        expr = sp.sympify(body.expr, locals=sympy_locals(body.var, x))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"invalid expression: {e}")

    dom = compute_domain(expr, x)
    return {"raw": sp.sstr(dom)}
