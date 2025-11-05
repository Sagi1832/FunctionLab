import re
from typing import List, Union


def fmt_inf(s: str) -> str:
    """Convert infinity symbols to display format."""
    if s == "oo":
        return "+∞"
    elif s == "-oo":
        return "−∞"
    else:
        return s


_INTERVAL_RE = re.compile(r"""^Interval\(\s*([^,]+)\s*,\s*([^)]+)\s*\)$""")

def _fmt_inf_token(tok: str) -> str:
    """Map 'oo'/'-oo' to ±∞, otherwise return stripped token unchanged."""
    tok = tok.strip()
    if tok == "oo":
        return "+∞"
    if tok == "-oo":
        return "−∞"
    return tok

def _fmt_pair(a: str, b: str) -> str:
    """Format a pair '(a, b)' with infinity normalization."""
    return f"({_fmt_inf_token(a)}, {_fmt_inf_token(b)})"

def fmt_value(v: Union[str, tuple, int, float]) -> str:
    """Format various value types into a compact display string."""
    if isinstance(v, str):
        m = _INTERVAL_RE.match(v)
        if m:
            a, b = m.group(1), m.group(2)
            return _fmt_pair(a, b)

        if v.startswith("(") and v.endswith(")"):
            inner = v[1:-1]
            parts = [p.strip() for p in inner.split(",")]
            if len(parts) == 2:
                return _fmt_pair(parts[0], parts[1])
            return "(" + ", ".join(_fmt_inf_token(p) for p in parts) + ")"

        return _fmt_inf_token(v)

    if isinstance(v, tuple):
        parts = [str(x) for x in v]
        if len(parts) == 2:
            return _fmt_pair(parts[0], parts[1])
        return "(" + ", ".join(_fmt_inf_token(p) for p in parts) + ")"

    if isinstance(v, (int, float)):
        return _fmt_inf_token(str(v))


    return _fmt_inf_token(str(v))


def join_disp(items: List[str]) -> str:
    """Join a list of strings with a comma and space."""
    return ", ".join(items)
