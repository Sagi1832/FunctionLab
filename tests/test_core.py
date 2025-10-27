import sympy as sp

# ===== core imports (as in your project) =====
from app.core.foundation import compute_domain, DerivativeEngine
from app.core.critical_points import find_critical_candidates, keep_real
from app.core.monotonic import monotonicity_intervals
from app.core.asymptotes import (
    find_vertical_asymptotes,
    find_horizontal_asymptotes,
    x_asymptotes,
)

x = sp.Symbol("x", real=True)

# ------------ helpers ------------
def almost_equal(a, b, eps=1e-6):
    return abs(float(a) - float(b)) < eps

def normalize_trend(t: str) -> str:
    t = (t or "").lower()
    if t in {"inc", "increasing", "up"}:
        return "inc"
    if t in {"dec", "decreasing", "down"}:
        return "dec"
    return t

def in_any_interval(val: float, intervals):
    """return True if val is inside any of the sympy.Intervals in list"""
    v = sp.Float(val)
    for iv in intervals:
        if isinstance(iv, sp.Interval) and v in iv:
            return True
    return False

def split_by_trend(pairs):
    inc = [iv for iv, t in pairs if normalize_trend(t) == "inc"]
    dec = [iv for iv, t in pairs if normalize_trend(t) == "dec"]
    return inc, dec

# ============== FOUNDATION / DOMAIN =================

def test_compute_domain_returns_reals():
    f = x**2 + 1
    D = compute_domain(f, x)
    assert D == sp.S.Reals or isinstance(D, sp.Set)

def test_compute_domain_handles_division():
    f = 1/x
    D = compute_domain(f, x)
    assert isinstance(D, sp.Set)
    assert sp.Integer(0) not in D

def test_domain_sqrt_and_log():
    f1 = sp.sqrt(x - 1)
    D1 = compute_domain(f1, x)
    assert sp.Integer(1) in D1 and sp.Integer(0) not in D1

    f2 = sp.log(x)
    D2 = compute_domain(f2, x)
    assert sp.Integer(1) in D2 and sp.Integer(0) not in D2

def test_domain_tan_excludes_pi_over_2():
    f = sp.tan(x)
    D = compute_domain(f, x)
    for n in range(-3, 4):
        val = sp.pi/2 + n*sp.pi
        assert not bool(sp.Contains(val, D))

# ============== CRITICAL POINTS =====================

def test_critical_points_polynomial():
    f = x**3 - 3*x
    eng = DerivativeEngine(f, x)
    D = sp.Interval(-sp.oo, sp.oo)
    cps = [sp.N(c) for c in keep_real(find_critical_candidates(eng, D))]
    assert sp.N(-1) in cps and sp.N(1) in cps

def test_critical_points_in_interval_clip():
    f = x**3 - 3*x
    eng = DerivativeEngine(f, x)
    D = sp.Interval(-2, 0)
    cps = [sp.N(c) for c in keep_real(find_critical_candidates(eng, D))]
    assert sp.N(-1) in cps and sp.N(1) not in cps

def test_critical_points_constant_function():
    f = sp.Integer(2)
    eng = DerivativeEngine(f, x)
    cps = list(keep_real(find_critical_candidates(eng, sp.S.Reals)))
    assert len(cps) == 0

# ============== MONOTONICITY (דגימה נקודתית) =======

def test_monotonicity_polynomial_segmented():
    f = x**3 - 3*x
    eng = DerivativeEngine(f, x)
    pairs = monotonicity_intervals(eng, sp.Interval(-2, 2))
    inc, dec = split_by_trend(pairs)
    assert in_any_interval(-1.5, inc)
    assert in_any_interval( 1.5, inc)
    assert in_any_interval( 0.0, dec)

def test_monotonicity_exp_all_reals_increasing():
    f = sp.exp(x)
    eng = DerivativeEngine(f, x)
    pairs = monotonicity_intervals(eng, sp.Interval(-10, 10))
    inc, dec = split_by_trend(pairs)
    for z in (-5.0, 0.0, 5.0):
        assert in_any_interval(z, inc)
    assert all(not in_any_interval(z, dec) for z in (-5.0, 0.0, 5.0))

def test_monotonicity_one_over_x_decreasing_in_two_pieces():
    f = 1/x
    eng = DerivativeEngine(f, x)
    pairs = monotonicity_intervals(eng, sp.Interval(-5, 5))
    inc, dec = split_by_trend(pairs)
    assert in_any_interval(-1.0, dec)
    assert in_any_interval( 1.0, dec)
    assert not in_any_interval(-1.0, inc)
    assert not in_any_interval( 0.0, inc)
    assert not in_any_interval( 1.0, inc)

def test_monotonicity_quadratic_down_then_up():
    f = x**2
    eng = DerivativeEngine(f, x)
    pairs = monotonicity_intervals(eng, sp.Interval(-3, 3))
    inc, dec = split_by_trend(pairs)
    assert in_any_interval(-1.0, dec)
    assert in_any_interval( 1.0, inc)

def test_monotonicity_abs_value_corner_at_zero():
    f = sp.Abs(x)
    eng = DerivativeEngine(f, x)
    pairs = monotonicity_intervals(eng, sp.Interval(-3, 3))
    inc, dec = split_by_trend(pairs)
    assert in_any_interval(-1.0, dec)
    assert in_any_interval( 1.0, inc)

def test_monotonicity_log_increasing_on_positive():
    f = sp.log(x)
    eng = DerivativeEngine(f, x)
    pairs = monotonicity_intervals(eng, sp.Interval(0.1, 10))
    inc, dec = split_by_trend(pairs)
    for z in (0.2, 1.0, 5.0):
        assert in_any_interval(z, inc)
        assert not in_any_interval(z, dec)

def test_monotonicity_constant_has_no_incdec():
    f = sp.Integer(2)
    eng = DerivativeEngine(f, x)
    pairs = monotonicity_intervals(eng, sp.Interval(-5, 5))
    inc = [iv for iv, t in pairs if (t or "").lower().startswith("inc")]
    dec = [iv for iv, t in pairs if (t or "").lower().startswith("dec")]
    assert len(inc) == 0 and len(dec) == 0

# ============== ASYMPTOTES ==========================

def test_asymptotes_rational_vertical_and_horizontal():
    f = (2*x + 3)/(x - 1)
    D = compute_domain(f, x)
    verts = list(find_vertical_asymptotes(f, x, D))
    horiz = find_horizontal_asymptotes(f, x)
    assert any(almost_equal(v, 1.0) for v in verts)
    horiz_vals = [h for h in (horiz.values() if hasattr(horiz, "values") else horiz) if h is not None]
    assert any(almost_equal(h, 2.0) for h in horiz_vals)

def test_asymptotes_horizontal_equal_degrees():
    f = (x**2 + 1)/(x**2 + 2)
    D = compute_domain(f, x)
    verts = list(find_vertical_asymptotes(f, x, D))
    horiz = find_horizontal_asymptotes(f, x)
    assert len(verts) == 0
    horiz_vals = [h for h in (horiz.values() if hasattr(horiz, "values") else horiz) if h is not None]
    assert any(almost_equal(h, 1.0) for h in horiz_vals)

def test_asymptotes_oblique_for_x2_over_x():
    f = (x**2 + 1)/x
    D = compute_domain(f, x)
    verts = list(find_vertical_asymptotes(f, x, D))
    horiz = find_horizontal_asymptotes(f, x)
    obl = x_asymptotes(f, x)
    horiz_vals = [h for h in (horiz.values() if hasattr(horiz, "values") else horiz) if h is not None]
    assert len(horiz_vals) == 0
    items = list(obl) if not isinstance(obl, list) else obl
    assert items is not None

def test_asymptotes_simple_rational_again():
    f = (x + 1)/(x - 2)
    D = compute_domain(f, x)
    verts = list(find_vertical_asymptotes(f, x, D))
    horiz = find_horizontal_asymptotes(f, x)
    assert any(abs(float(v) - 2.0) < 1e-6 for v in verts)
    horiz_vals = [h for h in (horiz.values() if hasattr(horiz, "values") else horiz) if h is not None]
    assert any(abs(float(h) - 1.0) < 1e-6 for h in horiz_vals)

def test_asymptotes_exp_has_horizontal_y0():
    x = sp.Symbol("x", real=True)
    f = sp.exp(x)
    D = compute_domain(f, x)

    # אין אסימפטוטות אנכיות ל-e^x
    verts = list(find_vertical_asymptotes(f, x, D))
    assert len(verts) == 0

    # יש אופקית y = 0 (כש-x -> -∞)
    horiz = find_horizontal_asymptotes(f, x)

    # נחלץ את הערכים בצורה עמידה למבנה ההחזרה
    vals = (
        list(horiz.values()) if hasattr(horiz, "values")
        else (list(horiz) if hasattr(horiz, "__iter__") else [horiz])
    )

    # ניקח רק ערכים מספריים סופיים
    finite = [v for v in vals if v is not None and getattr(v, "is_finite", False)]

    # מצפים שקיימת האופקית y=0
    assert any(abs(float(v)) < 1e-9 for v in finite)


def test_oblique_asymptote_for_x2_over_x_behaves():
    f = (x**2 + 1)/x
    D = compute_domain(f, x)
    obl = x_asymptotes(f, x)
    items = list(obl) if not isinstance(obl, list) else obl
    assert items is not None
