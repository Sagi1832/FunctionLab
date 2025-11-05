# app/api/all_routes/func_library/extrema_and_monotonic_route.py
from typing import Dict, List, Tuple
import sympy as sp
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.api.adapters import sympy_locals, sstr_ln
from app.core.foundation.derivative import DerivativeEngine
from app.core.critical_points.true_critical_candidates import find_critical_candidates_simple
from app.core.critical_points.extreme_points import classify_extrema_from_monotonic
from app.core.monotonic import monotonicity_intervals
from app.api.all_routes.func_library.extrema_and_mono.helpers import _mk_interval, _interval_to_str, _point_to_str, _monotonic_output


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
def extrema_and_monotonic_endpoint(body: ExtremaMonoIn) -> ExtremaMonoOut:
    try:
        x = sp.Symbol(body.var, real=True)
        f = sp.sympify(body.expr, locals=sympy_locals(body.var, x))

        iv = _mk_interval(body.interval, body.closed)

        eng = DerivativeEngine(f, x)

        candidates = find_critical_candidates_simple(
            eng.expr, x, interval=iv, require_interval_if_infinite=False
        )

        mono_list = monotonicity_intervals(eng, interval=iv)  

        monotonic_out = _monotonic_output(eng, iv)
        mono_map: Dict[sp.Interval, str] = {seg: str(sign) for (seg, sign) in mono_list}

        classified = classify_extrema_from_monotonic(f, x, candidates, mono_map)
        extrema_out = [
            ExtremumOut(point=_point_to_str(x0, y0), label=lab)
            for (x0, y0), lab in classified.items()
        ]

        return ExtremaMonoOut(monotonic=monotonic_out, extrema=extrema_out)

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"invalid input: {e}")
