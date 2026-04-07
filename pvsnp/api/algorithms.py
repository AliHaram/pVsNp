from __future__ import annotations
from fastapi import APIRouter, Request, UploadFile, File, HTTPException
from pvsnp.engine.loader import parse_metadata

router = APIRouter()


@router.get("")
async def list_algorithms(request: Request):
    db = request.app.state.db
    rows = await db.fetch_all(
        "SELECT id, name, author, description, category, filename, created_at FROM algorithms ORDER BY created_at DESC"
    )
    return rows


@router.post("", status_code=201)
async def upload_algorithm(request: Request, file: UploadFile = File(...)):
    db = request.app.state.db
    source = (await file.read()).decode("utf-8")
    meta = parse_metadata(source)
    if not meta["name"]:
        meta["name"] = file.filename.replace(".py", "")

    # Save file to algorithms dir
    algo_dir = request.app.state.algorithms_dir
    filepath = algo_dir / file.filename
    filepath.write_text(source)

    algo_id = await db.execute(
        "INSERT INTO algorithms (name, author, description, category, filename, source_code) VALUES (?, ?, ?, ?, ?, ?)",
        (meta["name"], meta["author"], meta["description"], meta["category"], file.filename, source),
    )
    return {
        "id": algo_id,
        "name": meta["name"],
        "author": meta["author"],
        "description": meta["description"],
        "category": meta["category"],
        "filename": file.filename,
    }


@router.get("/{algorithm_id}")
async def get_algorithm(request: Request, algorithm_id: int):
    db = request.app.state.db
    row = await db.fetch_one("SELECT * FROM algorithms WHERE id = ?", (algorithm_id,))
    if not row:
        raise HTTPException(status_code=404, detail="Algorithm not found")
    return row


@router.delete("/{algorithm_id}", status_code=204)
async def delete_algorithm(request: Request, algorithm_id: int):
    db = request.app.state.db
    row = await db.fetch_one("SELECT filename FROM algorithms WHERE id = ?", (algorithm_id,))
    if not row:
        raise HTTPException(status_code=404, detail="Algorithm not found")
    await db.execute("DELETE FROM algorithms WHERE id = ?", (algorithm_id,))
