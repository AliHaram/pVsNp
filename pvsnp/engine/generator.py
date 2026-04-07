# pvsnp/engine/generator.py
from __future__ import annotations
import math
import random
from typing import Optional


def _euclidean_matrix(points: list) -> list:
    n = len(points)
    matrix = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            dx = points[i][0] - points[j][0]
            dy = points[i][1] - points[j][1]
            d = math.sqrt(dx * dx + dy * dy)
            matrix[i][j] = d
            matrix[j][i] = d
    return matrix


def _random_uniform(n: int, rng: random.Random) -> list:
    return [[rng.random(), rng.random()] for _ in range(n)]


def _clustered(n: int, rng: random.Random) -> list:
    num_clusters = max(2, n // 5)
    centers = [[rng.random(), rng.random()] for _ in range(num_clusters)]
    points = []
    for i in range(n):
        center = centers[i % num_clusters]
        points.append([
            max(0, min(1, center[0] + rng.gauss(0, 0.05))),
            max(0, min(1, center[1] + rng.gauss(0, 0.05))),
        ])
    return points


def _grid(n: int, rng: random.Random) -> list:
    side = math.isqrt(n)
    if side * side < n:
        side += 1
    points = []
    for i in range(n):
        row = i // side
        col = i % side
        points.append([col / max(side - 1, 1), row / max(side - 1, 1)])
    return points


def _adversarial(n: int, rng: random.Random) -> list:
    points = []
    for i in range(n):
        angle = 2 * math.pi * i / n
        r = 0.4 + 0.1 * rng.random()
        points.append([0.5 + r * math.cos(angle), 0.5 + r * math.sin(angle)])
    return points


_GENERATORS = {
    "random": _random_uniform,
    "clustered": _clustered,
    "grid": _grid,
    "adversarial": _adversarial,
}


def generate_instance(
    instance_type: str, n: int, seed: Optional[int] = None
) -> tuple:
    rng = random.Random(seed)
    generator = _GENERATORS.get(instance_type)
    if generator is None:
        raise ValueError(f"Unknown instance type: {instance_type}. Options: {list(_GENERATORS.keys())}")
    points = generator(n, rng)
    matrix = _euclidean_matrix(points)
    return points, matrix
