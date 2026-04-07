from __future__ import annotations
import json
from fastapi import APIRouter, Request, HTTPException
from pvsnp.models.schemas import CounterexampleHuntRequest
from pvsnp.engine.counterexample import hunt_counterexamples

router = APIRouter()


@router.post("/hunt", status_code=201)
async def hunt(request: Request, body: CounterexampleHuntRequest):
    db = request.app.state.db
    algo = await db.fetch_one("SELECT * FROM algorithms WHERE id = ?", (body.algorithm_id,))
    if not algo:
        raise HTTPException(status_code=404, detail="Algorithm not found")

    # Load the solve function from source
    namespace = {}
    exec(algo["source_code"], namespace)
    solve_fn = namespace.get("solve")
    if not solve_fn:
        raise HTTPException(status_code=400, detail="Algorithm has no solve function")

    found = hunt_counterexamples(
        solve_fn=solve_fn,
        strategy=body.strategy,
        count=body.count,
        max_n=body.max_n,
    )

    results = []
    for ce in found:
        # Store instance
        inst_id = await db.execute(
            "INSERT INTO instances (name, instance_type, n, points, distance_matrix) VALUES (?, ?, ?, ?, ?)",
            (f"counterexample_n{ce['n']}", "counterexample", ce["n"],
             json.dumps(ce["points"]), json.dumps(ce["distance_matrix"])),
        )
        # Store counterexample
        ce_id = await db.execute(
            """INSERT INTO counterexamples
            (algorithm_id, instance_id, algorithm_tour, algorithm_tour_length, optimal_tour, optimal_tour_length)
            VALUES (?, ?, ?, ?, ?, ?)""",
            (body.algorithm_id, inst_id,
             json.dumps(ce["algorithm_tour"]), ce["algorithm_tour_length"],
             json.dumps(ce["optimal_tour"]), ce["optimal_tour_length"]),
        )
        results.append({
            "id": ce_id,
            "algorithm_id": body.algorithm_id,
            "instance_id": inst_id,
            "algorithm_tour": ce["algorithm_tour"],
            "algorithm_tour_length": ce["algorithm_tour_length"],
            "optimal_tour": ce["optimal_tour"],
            "optimal_tour_length": ce["optimal_tour_length"],
        })

    return results


@router.get("")
async def list_counterexamples(request: Request):
    db = request.app.state.db
    rows = await db.fetch_all(
        "SELECT * FROM counterexamples ORDER BY created_at DESC"
    )
    for r in rows:
        r["algorithm_tour"] = json.loads(r["algorithm_tour"])
        r["optimal_tour"] = json.loads(r["optimal_tour"])
    return rows
