from typing import List, Optional
import sympy as sp

def solve_raw_roots(
    fprime: sp.Expr,
    var: sp.Symbol,
    interval: Optional[sp.Interval] = None,
    *,
    require_interval_if_infinite: bool = True,
    ) -> List[sp.Expr]:
    """Solve f'(x)=0. If interval is given, solve only on it; otherwise on R.
    Raises if solution set on R is not finite and require_interval_if_infinite=True.
    """
    if interval is not None:
        solset = sp.solveset(sp.Eq(fprime, 0), var, domain=interval)
        return list(solset) if isinstance(solset, sp.FiniteSet) else []

    solset = sp.solveset(sp.Eq(fprime, 0), var, domain=sp.S.Reals)
    if isinstance(solset, sp.FiniteSet):
        return list(solset)

    if require_interval_if_infinite:
        raise ValueError("f'=0 has non-finite/undetermined solution set on R - interval required.")
    return []

def keep_real(roots: List[sp.Expr], tol: float = 1e-10) -> List[sp.Expr]:
    """Return only real roots (allowing tiny imaginary part <= tol)."""
    out: List[sp.Expr] = []
    for s in roots:
        try:
            if getattr(s, "is_real", None) is True:
                out.append(s)
            else:
                v = complex(s.evalf())
                if abs(v.imag) <= tol:
                    out.append(sp.nsimplify(v.real))
        except Exception:
            pass
    return out





        