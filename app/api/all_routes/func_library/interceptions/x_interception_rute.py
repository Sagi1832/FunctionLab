from typing import List, Optional, Tuple
import sympy as sp
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.api.adapters import sympy_locals, sstr_ln
from app.core.interception.x_interception import x_intercepts

router = APIRouter()


class XInterceptionIn(BaseModel):
    expr: str
    var: str = "x"
    interval: Optional[Tuple[float, float]] = Field(
        default=None, description="Optional interval [a,b] as two numbers"
    )
    closed: Optional[Tuple[bool, bool]] = (True, True)


class XInterceptionOut(BaseModel):
    # במקום xs: List[str] – מחזירים נקודות מלאות "(x, 0)"
    points: List[str]


@router.post("/x_intercepts", response_model=XInterceptionOut)
def x_intercepts_endpoint(body: XInterceptionIn) -> XInterceptionOut:
    try:
        # סמלים ופונקציה
        x = sp.Symbol(body.var, real=True)
        f = sp.sympify(body.expr, locals=sympy_locals(body.var, x))

        # אינטרוול אופציונלי
        iv = None
        if body.interval is not None:
            a, b = body.interval
            lc, rc = body.closed or (True, True)
            iv = sp.Interval(a, b, left_open=not lc, right_open=not rc)

        # פתרונות לחיתוך עם ציר ה-X (f(x)=0), מסוננים מול האינטרוול אם סופק
        sols = x_intercepts(f, x, interval=iv)

        # החזרה בפורמט נקודה מלאה "(x, 0)"
        points = [f"({sstr_ln(s)}, 0)" for s in sols]
        return XInterceptionOut(points=points)

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"invalid input: {e}")
