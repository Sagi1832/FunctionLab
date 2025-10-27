import sympy as sp

_TRIG_FUNCS = {sp.sin, sp.cos, sp.tan, sp.cot, sp.sec, sp.csc}

def _is_oscillatory(e: sp.Expr) -> bool:
    """ checking whether the user's function has any oscillatory (trigo) value """
    try:
        return any(e.has(fn) for fn in _TRIG_FUNCS)
    except Exception:
        return False


def needs_interval(expr: sp.Expr, var: sp.Symbol) -> bool:
    """ gives the call whether an interval is needed or not """

    fprime = sp.simplify(sp.diff(expr, var))
    try:
        solset = sp.solveset(sp.Eq(fprime, 0), var, domain=sp.S.Reals)
    except Exception:
        return True

    if isinstance(solset, sp.FiniteSet) or solset is sp.EmptySet:
        return _is_oscillatory(expr) or _is_oscillatory(fprime)

    return True
