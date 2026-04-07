# tests/test_curve_fitter.py
import pytest
from pvsnp.engine.curve_fitter import fit_complexity


def test_fit_linear():
    # Generate data that looks like O(n)
    data = [{"n": n, "time": n * 0.001 + 0.0001} for n in range(10, 110, 10)]
    fits = fit_complexity(data)
    best = fits[0]
    assert best["name"] == "O(n)"
    assert best["r_squared"] > 0.95


def test_fit_quadratic():
    data = [{"n": n, "time": (n ** 2) * 0.0001} for n in range(10, 110, 10)]
    fits = fit_complexity(data)
    best = fits[0]
    assert best["name"] == "O(n²)"
    assert best["r_squared"] > 0.95


def test_fit_n_log_n():
    import math
    data = [{"n": n, "time": n * math.log2(n) * 0.0001} for n in range(10, 110, 10)]
    fits = fit_complexity(data)
    best = fits[0]
    assert best["name"] in ("O(n log n)", "O(n)")  # These can be close at small n
    assert best["r_squared"] > 0.90


def test_fits_are_sorted_by_r_squared():
    data = [{"n": n, "time": (n ** 2) * 0.0001} for n in range(10, 110, 10)]
    fits = fit_complexity(data)
    r2_values = [f["r_squared"] for f in fits]
    assert r2_values == sorted(r2_values, reverse=True)


def test_fit_returns_all_classes():
    data = [{"n": n, "time": n * 0.001} for n in range(10, 60, 10)]
    fits = fit_complexity(data)
    names = [f["name"] for f in fits]
    assert "O(1)" in names
    assert "O(n)" in names
    assert "O(n²)" in names
    assert "O(n³)" in names
    assert "O(2^n)" in names
