import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from pvsnp.server import app, get_db
from pvsnp.db import Database
from pathlib import Path


@pytest_asyncio.fixture
async def client(tmp_path):
    db = Database(tmp_path / "test.db")
    await db.init()
    app.state.db = db
    app.state.algorithms_dir = tmp_path / "algorithms"
    app.state.algorithms_dir.mkdir()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    await db.close()


SAMPLE_ALGO = '''"""
name: Test Solver
author: tester
description: Always returns nodes in order
category: test
"""

def solve(distance_matrix):
    return list(range(len(distance_matrix)))
'''


@pytest.mark.asyncio
async def test_list_algorithms_empty(client):
    resp = await client.get("/api/algorithms")
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_upload_algorithm(client):
    resp = await client.post(
        "/api/algorithms",
        files={"file": ("test_solver.py", SAMPLE_ALGO, "text/x-python")},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Test Solver"
    assert data["author"] == "tester"


@pytest.mark.asyncio
async def test_list_algorithms_after_upload(client):
    await client.post(
        "/api/algorithms",
        files={"file": ("test_solver.py", SAMPLE_ALGO, "text/x-python")},
    )
    resp = await client.get("/api/algorithms")
    assert resp.status_code == 200
    assert len(resp.json()) == 1


@pytest.mark.asyncio
async def test_get_algorithm_by_id(client):
    create_resp = await client.post(
        "/api/algorithms",
        files={"file": ("test_solver.py", SAMPLE_ALGO, "text/x-python")},
    )
    algo_id = create_resp.json()["id"]
    resp = await client.get(f"/api/algorithms/{algo_id}")
    assert resp.status_code == 200
    assert resp.json()["name"] == "Test Solver"


@pytest.mark.asyncio
async def test_delete_algorithm(client):
    create_resp = await client.post(
        "/api/algorithms",
        files={"file": ("test_solver.py", SAMPLE_ALGO, "text/x-python")},
    )
    algo_id = create_resp.json()["id"]
    resp = await client.delete(f"/api/algorithms/{algo_id}")
    assert resp.status_code == 204
    resp = await client.get(f"/api/algorithms/{algo_id}")
    assert resp.status_code == 404
