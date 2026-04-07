import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from pvsnp.server import app
from pvsnp.db import Database


SAMPLE_ALGO = '''"""
name: Greedy Test
author: t
description: d
category: c
"""

def solve(distance_matrix):
    return list(range(len(distance_matrix)))
'''

SAMPLE_COMPLEXITY_ALGO = '''"""
name: Linear Search
input_generator: random_list
"""

def run(data):
    for x in data:
        pass
    return data
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
async def algo_id(client):
    resp = await client.post(
        "/api/algorithms",
        files={"file": ("greedy.py", SAMPLE_ALGO, "text/x-python")},
    )
    return resp.json()["id"]


@pytest.mark.asyncio
async def test_counterexample_hunt(client, algo_id):
    resp = await client.post("/api/counterexamples/hunt", json={
        "algorithm_id": algo_id,
        "strategy": "random",
        "count": 30,
        "max_n": 6,
    })
    assert resp.status_code == 201
    data = resp.json()
    assert isinstance(data, list)
    # A greedy "list(range(n))" solver should have counterexamples
    assert len(data) > 0


@pytest.mark.asyncio
async def test_counterexample_list(client, algo_id):
    await client.post("/api/counterexamples/hunt", json={
        "algorithm_id": algo_id,
        "strategy": "random",
        "count": 10,
        "max_n": 6,
    })
    resp = await client.get("/api/counterexamples")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_profiler_run(client, algo_id):
    resp = await client.post("/api/profiler/run", json={
        "algorithm_id": algo_id,
        "min_n": 4,
        "max_n": 12,
        "samples_per_size": 2,
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["status"] == "completed"
    assert len(data["data_points"]) > 0
    assert len(data["fits"]) > 0


@pytest.mark.asyncio
async def test_profiler_get(client, algo_id):
    create_resp = await client.post("/api/profiler/run", json={
        "algorithm_id": algo_id,
        "min_n": 4,
        "max_n": 10,
        "samples_per_size": 1,
    })
    run_id = create_resp.json()["id"]
    resp = await client.get(f"/api/profiler/{run_id}")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_complexity_analyze(client):
    resp = await client.post(
        "/api/complexity/analyze",
        data={"input_generator": "random_list"},
        files={"file": ("linear.py", SAMPLE_COMPLEXITY_ALGO, "text/x-python")},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["status"] == "completed"
    assert data["best_fit"] is not None


@pytest.mark.asyncio
async def test_complexity_get(client):
    create_resp = await client.post(
        "/api/complexity/analyze",
        data={"input_generator": "random_list"},
        files={"file": ("linear.py", SAMPLE_COMPLEXITY_ALGO, "text/x-python")},
    )
    analysis_id = create_resp.json()["id"]
    resp = await client.get(f"/api/complexity/{analysis_id}")
    assert resp.status_code == 200
