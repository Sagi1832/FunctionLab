#!/usr/bin/env python3
"""
Debug the derivative calculation
"""

import sympy as sp

x = sp.Symbol("x", real=True)

# Test different expressions
expr1 = sp.sympify("x + 1")
expr2 = sp.sympify("(x**2 - 1)/(x - 1)")
expr3 = sp.sympify("x**2 - 1")
expr4 = sp.sympify("x - 1")

print("=== Expression Tests ===")
print(f"x + 1: {expr1}")
print(f"(x**2 - 1)/(x - 1): {expr2}")
print(f"x**2 - 1: {expr3}")
print(f"x - 1: {expr4}")

print("\n=== Simplification Tests ===")
print(f"simplify(x + 1): {sp.simplify(expr1)}")
print(f"simplify((x**2 - 1)/(x - 1)): {sp.simplify(expr2)}")

print("\n=== Derivative Tests ===")
print(f"diff(x + 1, x): {sp.diff(expr1, x)}")
print(f"diff(simplify((x**2 - 1)/(x - 1)), x): {sp.diff(sp.simplify(expr2), x)}")

print("\n=== Manual Factorization ===")
# Manual factorization
num = x**2 - 1
den = x - 1
factored_num = sp.factor(num)
factored_den = sp.factor(den)
print(f"Numerator factored: {factored_num}")
print(f"Denominator factored: {factored_den}")
print(f"Fraction: {factored_num}/{factored_den}")

# Cancel the fraction
cancelled = sp.cancel(factored_num/factored_den)
print(f"Cancelled: {cancelled}")
print(f"Derivative of cancelled: {sp.diff(cancelled, x)}")

print("\n=== Check if expressions are equal ===")
simplified = sp.simplify(expr2)
print(f"simplify((x**2 - 1)/(x - 1)) == x + 1: {simplified == expr1}")
print(f"simplify((x**2 - 1)/(x - 1)) == x + 1: {sp.simplify(expr2) == sp.sympify('x + 1')}")
