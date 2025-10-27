from typing import Optional
import sympy as sp


def limit_at_point(f: sp.Expr, x: sp.Symbol, c: sp.Expr, side: str = '+') -> Optional[sp.Expr]:
    """ computes the limit at a certian given point (returns none if undefined) """
    try:
        if side == 'both':
            return sp.limit(f, x, c)
        if side not in ('+', '-'):
            raise ValueError("side must be '+', '-' or 'both'")
        return sp.limit(f, x, c, dir=side)
    except Exception:
        return None
