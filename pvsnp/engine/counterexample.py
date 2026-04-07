# pvsnp/engine/counterexample.py
from __future__ import annotations
import random
from typing import Callable, List, Tuple, Optional
from pvsnp.engine.generator import generate_instance
from pvsnp.engine.verifier import validate_tour, tour_length, find_optimal_tour


def hunt_counterexamples(
    solve_fn: Callable,
    strategy: str = "random",
    count: int = 100,
    max_n: int = 12,
    seed: Optional[int] = None,
) -> List[dict]:
    rng = random.Random(seed)
    counterexamples = []
    instances = _generate_test_instances(strategy, count, max_n, rng)

    for points, matrix, n in instances:
        try:
            algo_tour = solve_fn(matrix)
        except Exception:
            continue

        if not validate_tour(algo_tour, n=n):
            continue

        optimal_tour, optimal_length = find_optimal_tour(matrix)
        algo_length = tour_length(algo_tour, matrix)

        if algo_length > optimal_length + 1e-9:
            counterexamples.append({
                "points": points,
                "distance_matrix": matrix,
                "n": n,
                "algorithm_tour": algo_tour,
                "algorithm_tour_length": algo_length,
                "optimal_tour": optimal_tour,
                "optimal_tour_length": optimal_length,
            })

    return counterexamples


def _generate_test_instances(
    strategy: str, count: int, max_n: int, rng: random.Random
) -> List[Tuple[list, list, int]]:
    instances = []
    if strategy == "random":
        for _ in range(count):
            n = rng.randint(4, min(max_n, 12))
            seed = rng.randint(0, 2**31)
            points, matrix = generate_instance("random", n=n, seed=seed)
            instances.append((points, matrix, n))
    elif strategy == "structured":
        types = ["random", "clustered", "grid", "adversarial"]
        for i in range(count):
            n = rng.randint(4, min(max_n, 12))
            t = types[i % len(types)]
            seed = rng.randint(0, 2**31)
            points, matrix = generate_instance(t, n=n, seed=seed)
            instances.append((points, matrix, n))
    else:
        raise ValueError(f"Unknown strategy: {strategy}")
    return instances
