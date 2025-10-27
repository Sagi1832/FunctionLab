from typing import Optional, Tuple
import sympy as sp
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.core.interception.y_interception import y_intercept
from app.api.adapters import sympy_locals, sstr_ln

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
def y_intercepts_endpoint(body: YInterceptionIn) -> YInterceptionOut:
    try:
        x = sp.Symbol(body.var, real=True)
        f = sp.sympify(body.expr, locals=sympy_locals(body.var, x))

        iv = None
        if body.interval is not None:
            a, b = body.interval
            lc, rc = body.closed or (True, True)
            iv = sp.Interval(a, b, left_open=not lc, right_open=not rc)

        y0 = y_intercept(f, x, interval=iv)
        point = None if y0 is None else f"(0, {sstr_ln(y0)})"
        return YInterceptionOut(point=point)

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"invalid input: {e}")
