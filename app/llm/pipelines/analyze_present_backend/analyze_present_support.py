# app/llm/pipelines/analyze_present_support.py
from __future__ import annotations
from typing import Dict, Any, List, Tuple, Optional

from app.llm.schemas.analyze import AnalyzeResult, Action
from app.llm.agents.presenter_llm.agent import LLMPresenter

# --- formatting helpers (asymptotes & holes) ---

def _fmt_x_asymptotes(vertical) -> List[str]:
    vs = vertical or []
    return [f"x = {v}" for v in vs]

def _fmt_y_asymptotes(horizontal) -> Dict[str, Optional[str]]:
    h = horizontal or {}
    left = h.get("left")
    right = h.get("right")
    return {
        "left": f"y = {left}" if left not in (None, "", []) else None,
        "right": f"y = {right}" if right not in (None, "", []) else None,
    }

def _fmt_holes(holes) -> List[str]:
    out: List[str] = []
    for h in (holes or []):
        if h is None:
            continue
        if isinstance(h, (list, tuple)) and len(h) == 2:
            hx, hy = h[0], h[1]
            out.append(f"({hx}, {hy})")
            continue
        if isinstance(h, dict) and "x" in h and "y" in h:
            out.append(f"({h['x']}, {h['y']})")
            continue
        out.append(str(h))
    return out

# --- monotonicity/extrema helpers ---

def _is_infinite_interval(s: str) -> bool:
    return "oo" in s

def _filter_monotonic_finite(monotonic: Optional[Dict[str, str]]) -> Dict[str, str]:
    m = monotonic or {}
    return {iv: kind for iv, kind in m.items() if not _is_infinite_interval(iv)}

def _split_monotonic(monotonic: Dict[str, str]) -> Tuple[List[str], List[str]]:
    dec = [iv for iv, kind in monotonic.items() if kind == "dec"]
    inc = [iv for iv, kind in monotonic.items() if kind == "inc"]
    return dec, inc

def _fmt_extrema(extrema: Optional[List]) -> str:
    xs: List[str] = []
    for e in (extrema or []):
        if isinstance(e, dict) and "point" in e and "label" in e:
            xs.append(f"{e['point']} - {e['label']}")
        else:
            xs.append(str(e))
    return ", ".join(xs) if xs else "None"

# --- presenter-friendly report filtering (optional utility) ---

def filter_report_for_action(report: Dict[str, Any], action: Action | str) -> Dict[str, Any]:
    """Keep ONLY the fields relevant to the requested action so the Presenter renders a single card."""
    action_key = action.value if isinstance(action, Action) else str(action)

    keep_map: Dict[str, List[str]] = {
        "derivative": ["derivative"],
        "domain": ["domain"],
        "x_intercepts": ["x_intercepts"],
        "y_intercepts": ["y_intercepts"],
        "asymptotes_and_holes": ["asymptotes", "holes"],
        "extrema_and_monotonic": ["monotonic", "extrema"],
    }
    keys = keep_map.get(action_key, [])
    return {k: v for k, v in report.items() if k in keys}

# --- present data builders ---

def _init_present_data(result: AnalyzeResult) -> Dict[str, Any]:
    """Create the base 'present' payload shared by all actions."""
    return {
        "title": f"Analysis summary for f({result.var}) = {result.expr}",
        "expr": result.expr,
        "var": result.var,
        "action": result.action.value,
        "warnings": result.warnings,
        "errors": result.errors,
        "report": result.report,
    }

def _attach_asymptotes_card(present: Dict[str, Any], result: AnalyzeResult) -> None:
    """Build the asymptotes/holes card and attach it to 'present'."""
    original_report = result.report or {}
    vertical = original_report.get("vertical")
    horizontal = original_report.get("horizontal")
    holes = original_report.get("holes")

    card: Dict[str, Any] = {
        "x_asymptotes": _fmt_x_asymptotes(vertical),
        "y_asymptotes": _fmt_y_asymptotes(horizontal),
        "holes": _fmt_holes(holes),
    }
    present["card"] = card

def _attach_extrema_card(present: Dict[str, Any], result: AnalyzeResult) -> None:
    """Build the extrema/monotonicity card and attach it; also populate doc_md."""
    original_report = result.report or {}
    finite_mono = _filter_monotonic_finite(original_report.get("monotonic"))
    dec_list, inc_list = _split_monotonic(finite_mono)
    ext_text = _fmt_extrema(original_report.get("extrema"))

    card = {
        "dec": dec_list,
        "inc": inc_list,
        "extrema": ext_text,
    }
    present["card"] = card

    dec_text = ", ".join(dec_list) if dec_list else "None"
    inc_text = ", ".join(inc_list) if inc_list else "None"
    present["doc_md"] = f"dec: {dec_text}\ninc: {inc_text}\nextrema: {ext_text}"

def _maybe_run_presenter(present: Dict[str, Any], result: AnalyzeResult, warnings: List[str]) -> None:
    """Run the LLM presenter and put its output into doc_md, with resilient fallbacks."""
    try:
        presenter = LLMPresenter()
        doc = presenter.run(result)
        if not doc:
            warnings.append("LLM presenter returned empty result")
            doc = "No presentable results were produced."
        present["doc_md"] = doc
    except Exception as exc:
        warnings.append(f"LLM presenter failed: {exc}")
        present.setdefault("doc_md", "No presentable results were produced.")
