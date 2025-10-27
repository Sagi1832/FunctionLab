from typing import Optional, Tuple, List, Dict
from pydantic import BaseModel, Field
import sympy as sp
from fastapi import APIRouter, HTTPException
from app.core.asymptotes.asymptotes_display import asymptotes_summary
from app.api.adapters import sympy_locals

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
def asymptotes_and_holes_endpoint(body: AsymptotesHolesIn) -> AsymptotesHolesOut:
    try:
        x = sp.Symbol(body.var, real=True)
        f = sp.sympify(body.expr, locals=sympy_locals(body.var, x))

        iv = None
        if body.interval is not None:
            a, b = body.interval
            lc, rc = body.closed or (True, True)
            iv = sp.Interval(a, b, left_open=not lc, right_open=not rc)

        res = asymptotes_summary(f, x, interval=iv)

        # אנכי כמחרוזות
        vertical_out = [sp.sstr(v) for v in res["vertical"]]

        # אופקי – שים לב: אנחנו מצפים ל-"left"/"right"
        h = res["horizontal"]
        horizontal_out = {
            "left":  (None if h.get("left")  is None else sp.sstr(h["left"])),
            "right": (None if h.get("right") is None else sp.sstr(h["right"])),
        }

        # חורים: הפורמט המבוקש "(x0, y0)"
        holes_out = [f"({sp.sstr(x0)}, {sp.sstr(y0)})" for (x0, y0) in res["holes"]]

        return AsymptotesHolesOut(
            vertical=vertical_out,
            horizontal=horizontal_out,
            holes=holes_out,
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"invalid input: {e}")



