# tests/test_algorithms.py
import pytest
from pvsnp.engine.verifier import validate_tour, tour_length, find_optimal_tour
from pvsnp.engine.generator import generate_instance


def _load_solve(module_path: str):
    import importlib
    mod = importlib.import_module(module_path)
    return mod.solve


@pytest.fixture
def small_instance():
    _, matrix = generate_instance("random", n=6, seed=42)
    return matrix


@pytest.fixture
def medium_instance():
    _, matrix = generate_instance("random", n=20, seed=42)
    return matrix


class TestBruteForce:
    def test_returns_valid_tour(self, small_instance):
        solve = _load_solve("pvsnp.algorithms.brute_force")
        tour = solve(small_instance)
        assert validate_tour(tour, n=6)

    def test_returns_optimal_tour(self, small_instance):
        solve = _load_solve("pvsnp.algorithms.brute_force")
        tour = solve(small_instance)
        _, optimal_length = find_optimal_tour(small_instance)
        assert abs(tour_length(tour, small_instance) - optimal_length) < 1e-9


class TestNearestNeighbor:
    def test_returns_valid_tour(self, medium_instance):
        solve = _load_solve("pvsnp.algorithms.nearest_neighbor")
        tour = solve(medium_instance)
        assert validate_tour(tour, n=20)

    def test_tour_is_reasonable(self, small_instance):
        solve = _load_solve("pvsnp.algorithms.nearest_neighbor")
        tour = solve(small_instance)
        _, optimal_length = find_optimal_tour(small_instance)
        length = tour_length(tour, small_instance)
        # Nearest neighbor should be within 2x optimal for small instances
        assert length < optimal_length * 2


class TestTwoOpt:
    def test_returns_valid_tour(self, medium_instance):
        solve = _load_solve("pvsnp.algorithms.two_opt")
        tour = solve(medium_instance)
        assert validate_tour(tour, n=20)

    def test_improves_on_greedy(self, small_instance):
        nn_solve = _load_solve("pvsnp.algorithms.nearest_neighbor")
        opt_solve = _load_solve("pvsnp.algorithms.two_opt")
        nn_length = tour_length(nn_solve(small_instance), small_instance)
        opt_length = tour_length(opt_solve(small_instance), small_instance)
        assert opt_length <= nn_length


class TestChristofides:
    def test_returns_valid_tour(self, medium_instance):
        solve = _load_solve("pvsnp.algorithms.christofides")
        tour = solve(medium_instance)
        assert validate_tour(tour, n=20)

    def test_within_1_5_optimal(self, small_instance):
        solve = _load_solve("pvsnp.algorithms.christofides")
        tour = solve(small_instance)
        _, optimal_length = find_optimal_tour(small_instance)
        length = tour_length(tour, small_instance)
        assert length <= optimal_length * 1.5 + 1e-9
