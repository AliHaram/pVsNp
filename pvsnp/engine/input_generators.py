# pvsnp/engine/input_generators.py
from __future__ import annotations
import random
import string
from typing import Optional


def generate_input(generator_type: str, n: int, seed: Optional[int] = None):
    rng = random.Random(seed)
    generators = {
        "random_list": _random_list,
        "sorted_list": _sorted_list,
        "reversed_list": _reversed_list,
        "random_string": _random_string,
        "random_graph": _random_graph,
    }
    gen = generators.get(generator_type)
    if gen is None:
        raise ValueError(
            f"Unknown generator: {generator_type}. Options: {list(generators.keys())}"
        )
    return gen(n, rng)


def _random_list(n: int, rng: random.Random) -> list:
    return [rng.randint(0, n * 10) for _ in range(n)]


def _sorted_list(n: int, rng: random.Random) -> list:
    return sorted(rng.randint(0, n * 10) for _ in range(n))


def _reversed_list(n: int, rng: random.Random) -> list:
    return sorted((rng.randint(0, n * 10) for _ in range(n)), reverse=True)


def _random_string(n: int, rng: random.Random) -> str:
    return "".join(rng.choices(string.ascii_lowercase, k=n))


def _random_graph(n: int, rng: random.Random) -> list:
    matrix = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            w = rng.random()
            matrix[i][j] = w
            matrix[j][i] = w
    return matrix
