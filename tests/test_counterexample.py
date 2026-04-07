# tests/test_counterexample.py
import pytest
from pvsnp.engine.counterexample import hunt_counterexamples


def _always_wrong_solver(distance_matrix):
    """Always returns nodes in order — usually suboptimal."""
    return list(range(len(distance_matrix)))


def _optimal_solver(distance_matrix):
    """Brute force — always optimal."""
    from pvsnp.engine.verifier import find_optimal_tour
    tour, _ = find_optimal_tour(distance_matrix)
    return tour


def test_finds_counterexample_for_bad_algo():
    results = hunt_counterexamples(
        solve_fn=_always_wrong_solver,
        strategy="random",
        count=50,
        max_n=6,
        seed=42,
    )
    assert len(results) > 0
    for ce in results:
        assert ce["algorithm_tour_length"] > ce["optimal_tour_length"]


def test_no_counterexample_for_optimal_algo():
    results = hunt_counterexamples(
        solve_fn=_optimal_solver,
        strategy="random",
        count=20,
        max_n=6,
        seed=42,
    )
    assert len(results) == 0


def test_structured_strategy():
    results = hunt_counterexamples(
        solve_fn=_always_wrong_solver,
        strategy="structured",
        count=20,
        max_n=8,
        seed=42,
    )
    assert len(results) > 0
