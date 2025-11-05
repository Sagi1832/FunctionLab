from __future__ import annotations
import re

_BASIC_REPLACEMENTS = [
    (r"(?<=\w)\s*(?=\()", ""),          
    (r"(\d)\s*([A-Za-z])", r"\1*\2"),   
    (r"([A-Za-z])\s+([A-Za-z])", r"\1*\2"), 
    (r"\^", r"**"),                     
]

_FUNC_FIXES = [
    (r"\bl\s*\*\s*n\s*\(", "log("),     
    (r"\bln\s*\(", "log("),             
]

def _apply_basic_replacements(s: str) -> str:
    """Apply basic replacements to the expression."""
    out = s
    for pat, rep in _BASIC_REPLACEMENTS:
        out = re.sub(pat, rep, out)
    return out

def _fix_functions(s: str) -> str:
    """Fix the functions in the expression."""
    out = s
    for pat, rep in _FUNC_FIXES:
        out = re.sub(pat, rep, out, flags=re.IGNORECASE)
    out = re.sub(r"(?<=\w)\s+(?=\()", "", out)
    return out

def _fix_roots(s: str) -> str:
    """Fix the roots in the expression."""
    out = s
    out = re.sub(r"√\s*\(", "(", out)           
    out = re.sub(r"√\s*([A-Za-z0-9_]+)", r"(\1)**(1/2)", out)
    return out

def _sanitize_expression(text: str, var: str) -> str:
    """Clean the LLM response to a SymPy-safe Python expression."""
    s = text.strip()

    s = re.sub(r"^```.*?\n", "", s, flags=re.DOTALL)
    s = re.sub(r"```$", "", s)
    s = s.strip()

    s = _apply_basic_replacements(s)
    s = _fix_functions(s)
    s = _fix_roots(s)

    s = re.sub(r"\s*\*\*\s*", "**", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def _fallback_normalize(expr: str, var: str) -> str:
    """Fallback normalize the expression."""
    s = expr
    s = _apply_basic_replacements(s)
    s = _fix_functions(s)
    s = _fix_roots(s)
    s = re.sub(r"\s*\*\*\s*", "**", s)
    return s.strip()