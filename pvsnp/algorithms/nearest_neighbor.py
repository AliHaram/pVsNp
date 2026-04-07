# pvsnp/algorithms/nearest_neighbor.py
"""
name: Nearest Neighbor
author: pvsnp
description: Greedy heuristic — always visit the closest unvisited node.
category: heuristic
"""


def solve(distance_matrix: list) -> list:
    n = len(distance_matrix)
    visited = [False] * n
    tour = [0]
    visited[0] = True
    for _ in range(n - 1):
        current = tour[-1]
        nearest = -1
        nearest_dist = float("inf")
        for j in range(n):
            if not visited[j] and distance_matrix[current][j] < nearest_dist:
                nearest = j
                nearest_dist = distance_matrix[current][j]
        tour.append(nearest)
        visited[nearest] = True
    return tour
