from __future__ import annotations
import json
from fastapi import APIRouter, Request, HTTPException
from pvsnp.models.schemas import InstanceGenerateRequest
from pvsnp.engine.generator import generate_instance

router = APIRouter()


@router.post("/generate", status_code=201)
async def generate_instances(request: Request, body: InstanceGenerateRequest):
    db = request.app.state.db
    results = []
    for i in range(body.count):
        points, matrix = generate_instance(body.instance_type, n=body.n)
        name = body.name or f"{body.instance_type}_{body.n}_{i}"
        instance_id = await db.execute(
            "INSERT INTO instances (name, instance_type, n, points, distance_matrix) VALUES (?, ?, ?, ?, ?)",
            (name, body.instance_type, body.n, json.dumps(points), json.dumps(matrix)),
        )
        results.append({
            "id": instance_id,
            "name": name,
            "instance_type": body.instance_type,
            "n": body.n,
        })
    return results


@router.get("")
async def list_instances(request: Request):
    db = request.app.state.db
    rows = await db.fetch_all(
        "SELECT id, name, instance_type, n, created_at FROM instances ORDER BY created_at DESC"
    )
    return rows


@router.get("/{instance_id}")
async def get_instance(request: Request, instance_id: int):
    db = request.app.state.db
    row = await db.fetch_one("SELECT * FROM instances WHERE id = ?", (instance_id,))
    if not row:
        raise HTTPException(status_code=404, detail="Instance not found")
    return {
        **row,
        "points": json.loads(row["points"]),
        "distance_matrix": json.loads(row["distance_matrix"]),
    }
