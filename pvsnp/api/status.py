from __future__ import annotations
import time
from pathlib import Path
from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/status")
async def get_status(request: Request):
    db = request.app.state.db
    algos = await db.fetch_one("SELECT COUNT(*) as count FROM algorithms")
    instances = await db.fetch_one("SELECT COUNT(*) as count FROM instances")
    db_size = Path(str(db.path)).stat().st_size if Path(str(db.path)).exists() else 0
    uptime = time.time() - request.app.state.start_time

    return {
        "workers_active": 0,
        "workers_total": 4,
        "algorithms_count": algos["count"],
        "instances_count": instances["count"],
        "db_size_bytes": db_size,
        "uptime_seconds": round(uptime, 1),
    }
