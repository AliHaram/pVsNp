# tests/test_generator.py
import pytest
import math
from pvsnp.engine.generator import generate_instance


def test_random_uniform_generates_n_points():
    points, matrix = generate_instance("random", n=10, seed=42)
    assert len(points) == 10
    assert len(matrix) == 10
    assert all(len(row) == 10 for row in matrix)


def test_random_uniform_points_in_unit_square():
    points, _ = generate_instance("random", n=50, seed=42)
    for x, y in points:
        assert 0 <= x <= 1
        assert 0 <= y <= 1


def test_distance_matrix_is_symmetric():
    _, matrix = generate_instance("random", n=8, seed=42)
    for i in range(8):
        for j in range(8):
            assert abs(matrix[i][j] - matrix[j][i]) < 1e-9


def test_distance_matrix_diagonal_is_zero():
    _, matrix = generate_instance("random", n=8, seed=42)
    for i in range(8):
        assert matrix[i][i] == 0.0


def test_clustered_generates_n_points():
    points, matrix = generate_instance("clustered", n=20, seed=42)
    assert len(points) == 20
    assert len(matrix) == 20


def test_grid_generates_correct_count():
    points, matrix = generate_instance("grid", n=9, seed=42)
    assert len(points) == 9
    assert len(matrix) == 9


def test_adversarial_generates_n_points():
    points, matrix = generate_instance("adversarial", n=10, seed=42)
    assert len(points) == 10
    assert len(matrix) == 10


def test_distances_match_euclidean():
    points, matrix = generate_instance("random", n=5, seed=42)
    for i in range(5):
        for j in range(5):
            dx = points[i][0] - points[j][0]
            dy = points[i][1] - points[j][1]
            expected = math.sqrt(dx * dx + dy * dy)
            assert abs(matrix[i][j] - expected) < 1e-9


def test_seed_reproducibility():
    p1, m1 = generate_instance("random", n=10, seed=123)
    p2, m2 = generate_instance("random", n=10, seed=123)
    assert p1 == p2
    assert m1 == m2
