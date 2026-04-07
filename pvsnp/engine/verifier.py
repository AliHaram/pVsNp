# pvsnp/engine/verifier.py
from __future__ import annotations
from itertools import permutations
from typing import Tuple


def validate_tour(tour: list, n: int) -> bool:
    if len(tour) != n:
        return False
    if set(tour) != set(range(n)):
        return False
    return True


def tour_length(tour: list, distance_matrix: list) -> float:
    total = 0.0
    n = len(tour)
    for i in range(n):
        total += distance_matrix[tour[i]][tour[(i + 1) % n]]
    return total


def find_optimal_tour(
    distance_matrix: list,
) -> Tuple[list, float]:
    n = len(distance_matrix)
    if n > 20:
        raise ValueError(f"Brute force is limited to n <= 20, got n={n}")
    best_tour = None
    best_length = float("inf")
    # Fix first node to 0 to eliminate rotational duplicates
    for perm in permutations(range(1, n)):
        candidate = [0] + list(perm)
        length = tour_length(candidate, distance_matrix)
        if length < best_length:
            best_length = length
            best_tour = candidate
    return best_tour, best_length
