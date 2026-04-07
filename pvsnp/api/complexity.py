from __future__ import annotations
import json
import statistics
from datetime import datetime, timezone
from fastapi import APIRouter, Request, UploadFile, File, Form, HTTPException
from pvsnp.engine.loader import parse_metadata
from pvsnp.engine.input_generators import generate_input
from pvsnp.engine.curve_fitter import fit_complexity
from pvsnp.worker import run_algorithm_subprocess

router = APIRouter()


@router.post("/analyze", status_code=201)
async def analyze_complexity(
    request: Request,
    file: UploadFile = File(...),
    input_generator: str = Form("random_list"),
):
    db = request.app.state.db
    source = (await file.read()).decode("utf-8")
    meta = parse_metadata(source)
    name = meta.get("name") or file.filename.replace(".py", "")

    analysis_id = await db.execute(
        "INSERT INTO complexity_analyses (name, source_code, input_generator, status) VALUES (?, ?, ?, ?)",
        (name, source, input_generator, "running"),
    )

    # Generate logarithmically-spaced sizes
    sizes = sorted(set(
        int(10 ** (i * (5 - 1) / 47 + 1)) for i in range(48)
    ))
    # Cap at 10000 for safety
    sizes = [s for s in sizes if s <= 10000]

    data_points = []
    for n in sizes:
        times = []
        for _ in range(5):
            input_data = generate_input(input_generator, n=n)
            # Use the worker with the "run" interface
            wrapper_code = source + "\n\ndef solve(data):\n    return run(data)\n"
            result = await run_algorithm_subprocess(wrapper_code, input_data, timeout=10)
            if result["status"] == "success":
                times.append(result["execution_time"])
        if times:
            data_points.append({"n": n, "time": statistics.median(times)})

    fits = fit_complexity(data_points) if len(data_points) >= 3 else []
    best_fit = fits[0]["name"] if fits else None
    best_fit_r2 = fits[0]["r_squared"] if fits else None

    now = datetime.now(timezone.utc).isoformat()
    await db.execute(
        "UPDATE complexity_analyses SET status = ?, results = ?, best_fit = ?, best_fit_r2 = ?, completed_at = ? WHERE id = ?",
        ("completed", json.dumps(data_points), best_fit, best_fit_r2, now, analysis_id),
    )

    return {
        "id": analysis_id,
        "name": name,
        "status": "completed",
        "input_generator": input_generator,
        "data_points": data_points,
        "fits": fits,
        "best_fit": best_fit,
        "best_fit_r2": best_fit_r2,
        "created_at": now,
        "completed_at": now,
    }


@router.get("/{analysis_id}")
async def get_analysis(request: Request, analysis_id: int):
    db = request.app.state.db
    row = await db.fetch_one("SELECT * FROM complexity_analyses WHERE id = ?", (analysis_id,))
    if not row:
        raise HTTPException(status_code=404, detail="Analysis not found")
    result = dict(row)
    result["data_points"] = json.loads(result["results"]) if result["results"] else []
    result["fits"] = fit_complexity(result["data_points"]) if len(result["data_points"]) >= 3 else []
    del result["results"]
    return result
