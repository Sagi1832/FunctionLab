# app/llm/prompts/presenter_llm_prompt.py
from __future__ import annotations

SYSTEM_PROMPT = """You are the FunctionLab Presenter.
Transform the given JSON (action, expr, var, report) into ONE compact plain-text block.

Hard rules:
- Output plain text only (no Markdown, no bullets, no code fences).
- NEVER infer or recompute; use only fields provided in the JSON, **except for the explicit filtering rules described below for extrema_and_monotonic.**
- Keep +∞ and −∞ symbols as requested below. If the input has 'oo', treat it as +∞.
- Never print slashes like "/ None". If a section is empty, print exactly "None".
- Join multiple items on the same line with ", ".
- Line breaks are allowed ONLY where stated below.
- If nothing presentable exists, output "No presentable results were produced."

Per-action formats:

1) derivative
- Format: f'(VAR) = DERIVATIVE
- Take the derivative string from report.raw (or report.derivative if raw is missing).
- If missing, put "None" after the equals sign.

2) domain
- If the domain is all reals, print exactly: ℝ  (accepted hints: "Reals", "S.Reals", "ℝ", "(-∞, +∞)")
- Otherwise, print the domain exactly from report.raw, but with:
  - Replace 'oo' with '+∞'
  - Replace '(-oo' with '(-∞'
  - If it is a single Interval like "Interval(0, oo)", print "(0, +∞)"
  - If multiple sets/intervals are given, join them with " ∪ "
- If nothing is present, print "None".

3) x_intercepts
- If points exist: "interception: (x1, 0), (x2, 0), ..."
- Else: "interception: none"

4) y_intercepts
- If a point exists: "interception: (0, y)"
- Else: "interception: none"

5) asymptotes_and_holes   (THREE lines, in this exact order)
- Line 1 (x-asymptotes): "x-asymptotes: ..." or "x-asymptotes: None"
  * If report.vertical is a list like ["0","2"], print "x = 0, x = 2" (add the "x = " prefix if missing).
- Line 2 (y-asymptotes): "y-asymptotes: left: L, right: R" if either side exists; otherwise "y-asymptotes: None"
  * Values must be printed exactly as provided (e.g., "0", "1", "−∞", "+∞").
- Line 3 (holes): "holes: ..." or "holes: None"
  * If report.holes is a list like ["(a, b)"], join by ", ".

6) extrema_and_monotonic   (THREE lines, in this exact order)
- From report.monotonic (a dict mapping interval-string -> "inc" | "dec"):
  * **When building the dec/inc lists, IGNORE any interval whose string contains "+∞" or "−∞". Do not print such intervals at all.**
  * dec: <all remaining intervals with value "dec"> or "None"
  * inc: <all remaining intervals with value "inc"> or "None"
- From report.extrema (list of objects like {"point":"(x, y)","type":"min|max"}):
  * extrema: "(x1, y1) - min, (x2, y2) - max" or "None"

Remember:
- No slashes. No " / None". Print "None" only when a section has no items.
- Use exactly the labels shown above: f'(...), ℝ, x-asymptotes, y-asymptotes, holes, dec, inc, extrema.
"""
def _filter_infinite_monotonic(monotonic: dict[str, str]) -> dict[str, str]:
    """
    Return a copy of the monotonic mapping with any intervals containing
    'oo' or '∞' removed. This is only for LLM presentation; the raw report
    from the engine must remain unchanged.
    """
    if not monotonic:
        return {}
    return {
        interval: kind
        for interval, kind in monotonic.items()
        if "oo" not in interval and "∞" not in interval
    }


def build_user_prompt(*, action: str, expr: str, var: str, report: dict) -> str:
    """
    Build the single user message the model sees. It contains only the minimal
    data required for formatting, as plain JSON text.
    
    For extrema_and_monotonic action, filters out monotonic intervals with
    infinite endpoints ('oo' or '∞') before sending to the LLM.
    """
    import json
    
    # Work on a copy of the report to avoid mutating the original
    report_copy = report.copy() if isinstance(report, dict) else (report or {})
    
    # Filter infinite monotonic intervals for LLM presentation only
    if action == "extrema_and_monotonic" and isinstance(report_copy, dict):
        monotonic_raw = report_copy.get("monotonic") or {}
        monotonic = _filter_infinite_monotonic(monotonic_raw)
        report_copy["monotonic"] = monotonic
    
    payload = {
        "action": action,
        "expr": expr,
        "var": var,
        "report": report_copy,
    }
    return json.dumps(payload, ensure_ascii=False)
