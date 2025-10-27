from typing import Dict, Union, Optional
import sympy as sp
from sympy.printing.str import StrPrinter

def sympy_locals(var: Union[str, Dict[str, sp.Symbol]],
                 sym: Optional[sp.Symbol] = None) -> Dict[str, sp.Symbol]:
    """ Returns a dictionary of symbols for sympify. """
    base: Dict[str, sp.Symbol] = {
        "E": sp.E, "e": sp.E,
        "pi": sp.pi, "oo": sp.oo,
        "ln": sp.log,         
        "abs": sp.Abs,
        "sqrt": sp.sqrt,
    }

    if isinstance(var, dict):
        return {**base, **var}

    if isinstance(var, str):
        # var הוא שם המשתנה הראשי (למשל "x")
        if sym is None:
            sym = sp.Symbol(var, real=True)
        out = base.copy()
        out[var] = sym
        return out

    raise TypeError("sympy_locals expects a variable name (str) or a dict")

class LnStrPrinter(StrPrinter):
    """Print log(...) as ln(...); log(arg, base) when יש בסיס כללי."""
    def _print_log(self, expr):  
        base = getattr(expr, "base", None)
        arg  = expr.args[0]
        if base is None or base is sp.E:
            return f"ln({self._print(arg)})"
        return f"log({self._print(arg)}, {self._print(base)})"

def sstr_ln(expr: sp.Expr) -> str:
    return LnStrPrinter().doprint(expr)
