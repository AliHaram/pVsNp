# pvsnp/algorithms/brute_force.py
"""
name: Brute Force
author: pvsnp
description: Exact solver via exhaustive permutation search. Optimal but O(n!).
category: exact
"""
from itertools import permutations


def solve(distance_matrix: list) -> list:
    n = len(distance_matrix)
    best_tour = None
    best_length = float("inf")
    for perm in permutations(range(1, n)):
        tour = [0] + list(perm)
        length = sum(
            distance_matrix[tour[i]][tour[(i + 1) % n]] for i in range(n)
        )
        if length < best_length:
            best_length = length
            best_tour = tour
    return best_tour
