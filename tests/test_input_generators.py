# tests/test_input_generators.py
import pytest
from pvsnp.engine.input_generators import generate_input


def test_random_list():
    data = generate_input("random_list", n=100, seed=42)
    assert isinstance(data, list)
    assert len(data) == 100


def test_sorted_list():
    data = generate_input("sorted_list", n=50, seed=42)
    assert data == sorted(data)


def test_reversed_list():
    data = generate_input("reversed_list", n=50, seed=42)
    assert data == sorted(data, reverse=True)


def test_random_string():
    data = generate_input("random_string", n=100, seed=42)
    assert isinstance(data, str)
    assert len(data) == 100


def test_random_graph():
    data = generate_input("random_graph", n=10, seed=42)
    assert len(data) == 10
    assert all(len(row) == 10 for row in data)


def test_seed_reproducibility():
    a = generate_input("random_list", n=50, seed=99)
    b = generate_input("random_list", n=50, seed=99)
    assert a == b


def test_unknown_generator_raises():
    with pytest.raises(ValueError):
        generate_input("nonexistent", n=10)
