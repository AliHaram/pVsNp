from __future__ import annotations
import json
import statistics
from datetime import datetime, timezone
from fastapi import APIRouter, Request, HTTPException
from pvsnp.models.schemas import ProfilerRunRequest
from pvsnp.worker import run_algorithm_subprocess
from pvsnp.engine.generator import generate_instance
from pvsnp.engine.curve_fitter import fit_complexity

router = APIRouter()


@router.post("/run", status_code=201)
async def run_profiler(request: Request, body: ProfilerRunRequest):
    db = request.app.state.db
    algo = await db.fetch_one("SELECT * FROM algorithms WHERE id = ?", (body.algorithm_id,))
    if not algo:
        raise HTTPException(status_code=404, detail="Algorithm not found")

    run_id = await db.execute(
        "INSERT INTO profiler_runs (algorithm_id, status, min_n, max_n) VALUES (?, ?, ?, ?)",
        (body.algorithm_id, "running", body.min_n, body.max_n),
    )

    data_points = []
    n = body.min_n
    while n <= body.max_n:
        times = []
        for _ in range(body.samples_per_size):
            _, matrix = generate_instance("random", n=n)
            result = await run_algorithm_subprocess(algo["source_code"], matrix, timeout=30)
            if result["status"] == "success":
                times.append(result["execution_time"])
        if times:
            data_points.append({"n": n, "time": statistics.median(times)})
        # Increase n: small steps early, larger steps later
        if n < 20:
            n += 2
        elif n < 50:
            n += 5
        else:
            n += 10

    fits = fit_complexity(data_points) if len(data_points) >= 3 else []
    best_fit = fits[0]["name"] if fits else None
    best_fit_r2 = fits[0]["r_squared"] if fits else None

    now = datetime.now(timezone.utc).isoformat()
    await db.execute(
        "UPDATE profiler_runs SET status = ?, results = ?, best_fit = ?, best_fit_r2 = ?, completed_at = ? WHERE id = ?",
        ("completed", json.dumps(data_points), best_fit, best_fit_r2, now, run_id),
    )

    return {
        "id": run_id,
        "algorithm_id": body.algorithm_id,
        "status": "completed",
        "min_n": body.min_n,
        "max_n": body.max_n,
        "data_points": data_points,
        "fits": fits,
        "best_fit": best_fit,
        "best_fit_r2": best_fit_r2,
        "created_at": now,
        "completed_at": now,
    }


@router.get("/{run_id}")
async def get_profiler_run(request: Request, run_id: int):
    db = request.app.state.db
    row = await db.fetch_one("SELECT * FROM profiler_runs WHERE id = ?", (run_id,))
    if not row:
        raise HTTPException(status_code=404, detail="Profiler run not found")
    result = dict(row)
    result["data_points"] = json.loads(result["results"]) if result["results"] else []
    result["fits"] = fit_complexity(result["data_points"]) if len(result["data_points"]) >= 3 else []
    del result["results"]
    return result
