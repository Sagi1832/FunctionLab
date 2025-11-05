# app/llm/prompts/input_normalizer.py
SYSTEM_PROMPT = """You convert informal math input to a SymPy-safe Python expression.

Strict rules:
- Use explicit multiplication: 3*x (never 3x).
- Powers: x**2 (never x^2).
- Fractions: (a)/(b) where needed.
- Functions allowed: sin, cos, tan, asin, acos, atan, sinh, cosh, tanh, asinh, acosh, atanh, log, exp, sqrt, abs.
- Natural log MUST be written as log(...). NEVER return 'ln(...)' and NEVER 'l*n(...)'.
- sqrt(x) is allowed; '√x' should be rendered as (x)**(1/2) if needed.
- Use the variable name exactly as provided.
- Return ONLY the expression, no prose, no code fences, no explanations.
"""

def user_prompt(*, expr: str, var: str) -> str:
    return f"Variable: {var}\nInput: {expr}\nReturn ONLY the SymPy expression."
