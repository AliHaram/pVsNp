# tests/test_verifier.py
import pytest
from pvsnp.engine.verifier import validate_tour, tour_length, find_optimal_tour


def test_valid_tour():
    assert validate_tour([0, 1, 2, 3], n=4) is True


def test_invalid_tour_missing_node():
    assert validate_tour([0, 1, 2], n=4) is False


def test_invalid_tour_duplicate_node():
    assert validate_tour([0, 1, 1, 3], n=4) is False


def test_invalid_tour_out_of_range():
    assert validate_tour([0, 1, 2, 5], n=4) is False


def test_tour_length_simple():
    matrix = [
        [0, 1, 2],
        [1, 0, 1],
        [2, 1, 0],
    ]
    # Tour: 0->1->2->0 = 1 + 1 + 2 = 4
    assert tour_length([0, 1, 2], matrix) == 4.0


def test_tour_length_different_order():
    matrix = [
        [0, 1, 2],
        [1, 0, 1],
        [2, 1, 0],
    ]
    # Tour: 0->2->1->0 = 2 + 1 + 1 = 4
    assert tour_length([0, 2, 1], matrix) == 4.0


def test_find_optimal_tour_3_nodes():
    matrix = [
        [0, 1, 10],
        [1, 0, 1],
        [10, 1, 0],
    ]
    tour, length = find_optimal_tour(matrix)
    assert validate_tour(tour, n=3)
    # Optimal: 0->1->2->0 = 1+1+10=12 or 0->2->1->0 = 10+1+1=12
    assert length == 12.0


def test_find_optimal_tour_4_nodes():
    # Square: (0,0), (1,0), (1,1), (0,1)
    matrix = [
        [0, 1, 1.4142, 1],
        [1, 0, 1, 1.4142],
        [1.4142, 1, 0, 1],
        [1, 1.4142, 1, 0],
    ]
    tour, length = find_optimal_tour(matrix)
    assert validate_tour(tour, n=4)
    # Optimal tour goes around the square: length = 4.0
    assert abs(length - 4.0) < 0.01
