import pytest
import pytest_asyncio
import json
from httpx import AsyncClient, ASGITransport
from starlette.testclient import TestClient
from pvsnp.server import app
from pvsnp.db import Database
from pvsnp.api.ws import manager


@pytest_asyncio.fixture
async def db(tmp_path):
    database = Database(tmp_path / "test.db")
    await database.init()
    app.state.db = database
    app.state.algorithms_dir = tmp_path / "algorithms"
    app.state.algorithms_dir.mkdir()
    yield database
    await database.close()


def test_ws_connect(db):
    client = TestClient(app)
    with client.websocket_connect("/api/ws") as ws:
        # Connection manager should track this
        assert True  # Connection succeeded


@pytest.mark.asyncio
async def test_broadcast(db):
    sent_messages = []

    class FakeWS:
        async def send_json(self, data):
            sent_messages.append(data)

    mgr = manager
    fake = FakeWS()
    mgr.connections.append(fake)
    await mgr.broadcast({"type": "test", "data": "hello"})
    assert len(sent_messages) == 1
    assert sent_messages[0]["type"] == "test"
    mgr.connections.remove(fake)
