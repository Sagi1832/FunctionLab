# app/api/all_routes/func_library/foundation_funcs/limits_route.py
from app.api.adapters import sympy_locals
import sympy as sp
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException
from typing import Literal, Optional
from app.core.foundation.limits import limit_at_point

router = APIRouter()

class LimitIn(BaseModel):
    side: Literal['+', '-', 'both'] = '+'
    expr: str
    var: str = "x"
    point: str

class LimitOut(BaseModel):
    side: Literal['+', '-', 'both'] = '+'
    value: Optional[str] = None
    left: Optional[str] = None
    right: Optional[str] = None
    equal: Optional[bool] = None
    raw: Optional[str] = None
    error: Optional[str] = None

@router.post("/limit", response_model=LimitOut)
def limit_endpoint(body: LimitIn):
    try:
        x = sp.Symbol(body.var, real=True)
        env = sympy_locals(body.var, x)

        f = sp.sympify(body.expr,  locals=env)
        c = sp.sympify(body.point, locals=env)   

        if body.side in ('+', '-'):
            v = limit_at_point(f, x, c, side=body.side)
            return LimitOut(
                side=body.side,
                value=None if v is None else sp.sstr(v)
            )
        else:  
            L = limit_at_point(f, x, c, side='-')
            R = limit_at_point(f, x, c, side='+')
            eq = (L is not None and R is not None and sp.simplify(L - R) == 0)
            return LimitOut(
                side='both',
                left=None if L is None else sp.sstr(L),
                right=None if R is None else sp.sstr(R),
                value=None if not eq else sp.sstr(L),
                equal=eq
            )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"invalid input: {e}")
