from __future__ import annotations
import sympy as sp

# ---------- Formatting ----------

def _fmt(v: sp.Expr) -> str:
    if v is sp.S.NegativeInfinity:
        return "-inf"
    if v is sp.S.Infinity:
        return "inf"
    try:
        return sp.sstr(sp.nsimplify(v))
    except Exception:
        return str(v)

def interval_key(a: sp.Expr, b: sp.Expr) -> str:
    """Return a stable string key for an open interval (a, b)."""
    if a is sp.S.NegativeInfinity:
        return f"(<- {_fmt(b)})"
    if b is sp.S.Infinity:
        return f"({_fmt(a)} -> )"
    return f"({_fmt(a)} -> {_fmt(b)})"


# ---------- Parsing ----------

def parse_key(k: str) -> sp.Interval:
    """
    Parse keys created by interval_key:
      '(<- b)'  -> (-oo, b)  (Lopen)
      '(a -> )' -> (a, +oo)  (Ropen)
      '(a -> b)'-> (a, b)    (open)

    Tolerates extra spaces and missing side (maps to ±oo).
    Raises ValueError with a clear message on malformed input.
    """
    s = k.strip()
    if not (s.startswith("(") and s.endswith(")")):
        raise ValueError(f"Bad key (missing outer parens): {k!r}")
    s = s[1:-1].strip()  # e.g. '<- b' | 'a -> ' | 'a -> b'

    # Left-infinite: '<- b'
    if s.lstrip().startswith("<-"):
        b_str = s[2:].strip()
        if not b_str:
            raise ValueError(f"Right bound missing in: {k!r}")
        b = sp.sympify(b_str)
        return sp.Interval.Lopen(sp.S.NegativeInfinity, b)

    # Right-infinite: 'a ->' (possibly with trailing spaces)
    if s.rstrip().endswith("->"):
        a_str = s[:-2].strip()
        if not a_str:
            raise ValueError(f"Left bound missing in: {k!r}")
        a = sp.sympify(a_str)
        return sp.Interval.Ropen(a, sp.S.Infinity)

    # General case: 'a -> b'
    parts = s.split("->", 1)
    if len(parts) != 2:
        raise ValueError(f"Bad key (missing '->'): {k!r}")

    a_str, b_str = parts[0].strip(), parts[1].strip()
    if not a_str:
        b = sp.sympify(b_str)
        return sp.Interval.Lopen(sp.S.NegativeInfinity, b)
    if not b_str:
        a = sp.sympify(a_str)
        return sp.Interval.Ropen(a, sp.S.Infinity)

    a = sp.sympify(a_str)
    b = sp.sympify(b_str)
    return sp.Interval.open(a, b)
