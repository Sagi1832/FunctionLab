import sympy as sp
from dataclasses import dataclass, field
from typing import Optional, Union

ExprLike = Union[str, sp.Expr]

def _to_expr(e: ExprLike) -> sp.Expr:
    return e if isinstance(e, sp.Expr) else sp.sympify(e)

@dataclass(slots=True)
class DerivativeEngine:
    expr: sp.Expr
    symbol: sp.Symbol = field(default_factory=lambda: sp.Symbol("x", real=True))
    _raw: Optional[sp.Expr] = field(default=None, init=False, repr=False)
    _simplified: Optional[sp.Expr] = field(default=None, init=False, repr=False)

    @classmethod
    def from_strings(cls, expr: ExprLike, var: Union[str, sp.Symbol, None] = None):
        """Creates a DerivativeEngine from a string expression."""
        x = var if isinstance(var, sp.Symbol) else sp.Symbol(var or "x", real=True)
        return cls(_to_expr(expr), x)

    def derive(self) -> sp.Expr:
        """Derives the expression."""
        if self._raw is not None:
            return self._raw
        f = sp.simplify(self.expr)
        self._raw = sp.diff(f, self.symbol)
        return self._raw

    def simplify_derivative(self) -> sp.Expr:
        """Simplifies the derivative."""
        if self._simplified is not None:
            return self._simplified
        self._simplified = sp.simplify(self.derive())
        return self._simplified
