from __future__ import annotations
import json
from datetime import datetime, timezone
from fastapi import APIRouter, Request, HTTPException
from pvsnp.models.schemas import BenchmarkRunRequest
from pvsnp.worker import run_algorithm_subprocess
from pvsnp.engine.verifier import validate_tour, tour_length, find_optimal_tour

router = APIRouter()


@router.post("/run", status_code=201)
async def run_benchmark(request: Request, body: BenchmarkRunRequest):
    db = request.app.state.db

    run_id = await db.execute(
        "INSERT INTO benchmark_runs (status) VALUES (?)", ("running",)
    )

    results = []
    for algo_id in body.algorithm_ids:
        algo = await db.fetch_one("SELECT * FROM algorithms WHERE id = ?", (algo_id,))
        if not algo:
            continue
        for inst_id in body.instance_ids:
            inst = await db.fetch_one("SELECT * FROM instances WHERE id = ?", (inst_id,))
            if not inst:
                continue

            matrix = json.loads(inst["distance_matrix"])
            worker_result = await run_algorithm_subprocess(
                algo["source_code"], matrix, timeout=60
            )

            tour = None
            length = None
            is_optimal = None
            error = None

            if worker_result["status"] == "success":
                tour = worker_result["tour"]
                n = len(matrix)
                if validate_tour(tour, n):
                    length = tour_length(tour, matrix)
                    if n <= 20:
                        _, opt_length = find_optimal_tour(matrix)
                        is_optimal = abs(length - opt_length) < 1e-9
                else:
                    error = "Invalid tour returned"
            else:
                error = worker_result.get("error", "Unknown error")

            result_id = await db.execute(
                """INSERT INTO benchmark_results
                (run_id, algorithm_id, instance_id, tour, tour_length, is_optimal, execution_time, error)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    run_id, algo_id, inst_id,
                    json.dumps(tour) if tour else None,
                    length, is_optimal,
                    worker_result.get("execution_time", 0),
                    error,
                ),
            )
            results.append({
                "id": result_id,
                "run_id": run_id,
                "algorithm_id": algo_id,
                "algorithm_name": algo["name"],
                "instance_id": inst_id,
                "tour": tour,
                "tour_length": length,
                "is_optimal": is_optimal,
                "execution_time": worker_result.get("execution_time", 0),
                "error": error,
            })

    now = datetime.now(timezone.utc).isoformat()
    await db.execute(
        "UPDATE benchmark_runs SET status = ?, completed_at = ? WHERE id = ?",
        ("completed", now, run_id),
    )

    return {"id": run_id, "status": "completed", "results": results, "created_at": now, "completed_at": now}


@router.get("/{run_id}")
async def get_benchmark(request: Request, run_id: int):
    db = request.app.state.db
    run = await db.fetch_one("SELECT * FROM benchmark_runs WHERE id = ?", (run_id,))
    if not run:
        raise HTTPException(status_code=404, detail="Benchmark run not found")
    results = await db.fetch_all(
        """SELECT br.*, a.name as algorithm_name FROM benchmark_results br
        JOIN algorithms a ON br.algorithm_id = a.id
        WHERE br.run_id = ?""",
        (run_id,),
    )
    for r in results:
        if r.get("tour"):
            r["tour"] = json.loads(r["tour"])
    return {**run, "results": results}


@router.get("")
async def list_benchmarks(request: Request):
    db = request.app.state.db
    return await db.fetch_all("SELECT * FROM benchmark_runs ORDER BY created_at DESC")
