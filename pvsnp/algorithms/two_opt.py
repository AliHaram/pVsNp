# pvsnp/algorithms/two_opt.py
"""
name: 2-Opt
author: pvsnp
description: Local search improvement — repeatedly reverse segments to shorten tour.
category: heuristic
"""


def solve(distance_matrix: list) -> list:
    n = len(distance_matrix)
    # Start with nearest neighbor
    visited = [False] * n
    tour = [0]
    visited[0] = True
    for _ in range(n - 1):
        current = tour[-1]
        nearest = min(
            (j for j in range(n) if not visited[j]),
            key=lambda j: distance_matrix[current][j],
        )
        tour.append(nearest)
        visited[nearest] = True

    # 2-opt improvement
    improved = True
    while improved:
        improved = False
        for i in range(1, n - 1):
            for j in range(i + 1, n):
                d_old = (
                    distance_matrix[tour[i - 1]][tour[i]]
                    + distance_matrix[tour[j]][tour[(j + 1) % n]]
                )
                d_new = (
                    distance_matrix[tour[i - 1]][tour[j]]
                    + distance_matrix[tour[i]][tour[(j + 1) % n]]
                )
                if d_new < d_old - 1e-10:
                    tour[i : j + 1] = reversed(tour[i : j + 1])
                    improved = True
    return tour
