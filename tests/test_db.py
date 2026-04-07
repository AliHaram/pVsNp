# tests/test_db.py
import pytest
import asyncio
from pathlib import Path
from pvsnp.db import Database


@pytest.fixture
async def db(tmp_path):
    database = Database(tmp_path / "test.db")
    await database.init()
    yield database
    await database.close()


@pytest.mark.asyncio
async def test_init_creates_tables(db):
    tables = await db.fetch_all(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    )
    table_names = [row["name"] for row in tables]
    assert "algorithms" in table_names
    assert "instances" in table_names
    assert "benchmark_runs" in table_names
    assert "benchmark_results" in table_names
    assert "counterexamples" in table_names
    assert "profiler_runs" in table_names
    assert "complexity_analyses" in table_names


@pytest.mark.asyncio
async def test_insert_and_fetch(db):
    await db.execute(
        "INSERT INTO algorithms (name, author, description, category, filename, source_code) VALUES (?, ?, ?, ?, ?, ?)",
        ("test_algo", "tester", "a test", "test", "test.py", "def solve(m): return [0]"),
    )
    rows = await db.fetch_all("SELECT * FROM algorithms")
    assert len(rows) == 1
    assert rows[0]["name"] == "test_algo"


@pytest.mark.asyncio
async def test_fetch_one(db):
    await db.execute(
        "INSERT INTO algorithms (name, author, description, category, filename, source_code) VALUES (?, ?, ?, ?, ?, ?)",
        ("algo1", "a", "d", "c", "f.py", "code"),
    )
    row = await db.fetch_one("SELECT * FROM algorithms WHERE name = ?", ("algo1",))
    assert row is not None
    assert row["author"] == "a"
