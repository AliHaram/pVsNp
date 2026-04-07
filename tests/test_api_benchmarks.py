import pytest
import pytest_asyncio
import json
from httpx import AsyncClient, ASGITransport
from pvsnp.server import app
from pvsnp.db import Database


SAMPLE_ALGO = '''"""
name: Test Solver
author: tester
description: Returns nodes in order
category: test
"""

def solve(distance_matrix):
    return list(range(len(distance_matrix)))
'''


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


@pytest_asyncio.fixture
async def algo_and_instance(client):
    algo_resp = await client.post(
        "/api/algorithms",
        files={"file": ("solver.py", SAMPLE_ALGO, "text/x-python")},
    )
    inst_resp = await client.post("/api/instances/generate", json={
        "instance_type": "random",
        "n": 5,
        "count": 1,
    })
    return algo_resp.json()["id"], inst_resp.json()[0]["id"]


@pytest.mark.asyncio
async def test_run_benchmark(client, algo_and_instance):
    algo_id, inst_id = algo_and_instance
    resp = await client.post("/api/benchmarks/run", json={
        "algorithm_ids": [algo_id],
        "instance_ids": [inst_id],
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["status"] == "completed"
    assert len(data["results"]) == 1
    assert data["results"][0]["tour"] is not None


@pytest.mark.asyncio
async def test_get_benchmark(client, algo_and_instance):
    algo_id, inst_id = algo_and_instance
    create_resp = await client.post("/api/benchmarks/run", json={
        "algorithm_ids": [algo_id],
        "instance_ids": [inst_id],
    })
    run_id = create_resp.json()["id"]
    resp = await client.get(f"/api/benchmarks/{run_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == run_id


@pytest.mark.asyncio
async def test_list_benchmarks(client, algo_and_instance):
    algo_id, inst_id = algo_and_instance
    await client.post("/api/benchmarks/run", json={
        "algorithm_ids": [algo_id],
        "instance_ids": [inst_id],
    })
    resp = await client.get("/api/benchmarks")
    assert resp.status_code == 200
    assert len(resp.json()) >= 1
