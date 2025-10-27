import sympy as sp

def compute_domain(expr: sp.Expr, x: sp.Symbol) -> sp.Set:
    """
    Computes the real domain of f(x) over R.
    Returns a SymPy Set (Interval / Union / FiniteSet / Complement, etc.).
    """
    dom = sp.calculus.util.continuous_domain(expr, x, sp.S.Reals)
    try:
         dom = sp.simplify(dom)
    except Exception:
        pass

    return dom 
    