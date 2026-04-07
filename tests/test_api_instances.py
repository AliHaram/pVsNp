import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from pvsnp.server import app
from pvsnp.db import Database


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


@pytest.mark.asyncio
async def test_generate_instances(client):
    resp = await client.post("/api/instances/generate", json={
        "instance_type": "random",
        "n": 10,
        "count": 3,
    })
    assert resp.status_code == 201
    data = resp.json()
    assert len(data) == 3
    assert data[0]["n"] == 10


@pytest.mark.asyncio
async def test_list_instances(client):
    await client.post("/api/instances/generate", json={
        "instance_type": "random",
        "n": 5,
        "count": 2,
    })
    resp = await client.get("/api/instances")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


@pytest.mark.asyncio
async def test_get_instance_by_id(client):
    create_resp = await client.post("/api/instances/generate", json={
        "instance_type": "clustered",
        "n": 8,
        "count": 1,
    })
    instance_id = create_resp.json()[0]["id"]
    resp = await client.get(f"/api/instances/{instance_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["points"]) == 8
    assert len(data["distance_matrix"]) == 8
