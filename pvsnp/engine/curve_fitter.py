# pvsnp/engine/curve_fitter.py
from __future__ import annotations
import math
import numpy as np
from scipy.optimize import curve_fit


def _constant(n, a):
    return np.full_like(n, a, dtype=float)


def _log_n(n, a, b):
    return a * np.log2(n) + b


def _linear(n, a, b):
    return a * n + b


def _n_log_n(n, a, b):
    return a * n * np.log2(n) + b


def _quadratic(n, a, b):
    return a * n ** 2 + b


def _cubic(n, a, b):
    return a * n ** 3 + b


def _exponential(n, a, b):
    return a * 2.0 ** (n * b)


_MODELS = [
    ("O(1)", _constant, 1),
    ("O(log n)", _log_n, 2),
    ("O(n)", _linear, 2),
    ("O(n log n)", _n_log_n, 2),
    ("O(n²)", _quadratic, 2),
    ("O(n³)", _cubic, 2),
    ("O(2^n)", _exponential, 2),
]


def _r_squared(y_actual: np.ndarray, y_predicted: np.ndarray) -> float:
    ss_res = np.sum((y_actual - y_predicted) ** 2)
    ss_tot = np.sum((y_actual - np.mean(y_actual)) ** 2)
    if ss_tot == 0:
        return 1.0 if ss_res == 0 else 0.0
    return 1.0 - ss_res / ss_tot


def fit_complexity(data: list) -> list:
    ns = np.array([d["n"] for d in data], dtype=float)
    times = np.array([d["time"] for d in data], dtype=float)

    results = []
    for name, func, n_params in _MODELS:
        try:
            if n_params == 1:
                popt, _ = curve_fit(func, ns, times, p0=[np.mean(times)], maxfev=5000)
            else:
                popt, _ = curve_fit(func, ns, times, p0=[1e-6] * n_params, maxfev=5000)
            predicted = func(ns, *popt)
            r2 = _r_squared(times, predicted)
            results.append({"name": name, "r_squared": round(float(r2), 6)})
        except (RuntimeError, OverflowError, ValueError):
            results.append({"name": name, "r_squared": 0.0})

    results.sort(key=lambda x: x["r_squared"], reverse=True)
    return results
