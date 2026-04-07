# pvsnp/db.py
from __future__ import annotations
import aiosqlite
from pathlib import Path
from typing import Optional

SCHEMA = """
CREATE TABLE IF NOT EXISTS algorithms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    author TEXT DEFAULT '',
    description TEXT DEFAULT '',
    category TEXT DEFAULT '',
    filename TEXT NOT NULL,
    source_code TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS instances (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT DEFAULT '',
    instance_type TEXT NOT NULL,
    n INTEGER NOT NULL,
    points TEXT NOT NULL,
    distance_matrix TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS benchmark_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS benchmark_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER NOT NULL REFERENCES benchmark_runs(id),
    algorithm_id INTEGER NOT NULL REFERENCES algorithms(id),
    instance_id INTEGER NOT NULL REFERENCES instances(id),
    tour TEXT,
    tour_length REAL,
    is_optimal INTEGER,
    execution_time REAL,
    error TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS counterexamples (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    algorithm_id INTEGER NOT NULL REFERENCES algorithms(id),
    instance_id INTEGER NOT NULL REFERENCES instances(id),
    algorithm_tour TEXT NOT NULL,
    algorithm_tour_length REAL NOT NULL,
    optimal_tour TEXT NOT NULL,
    optimal_tour_length REAL NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS profiler_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    algorithm_id INTEGER NOT NULL REFERENCES algorithms(id),
    status TEXT NOT NULL DEFAULT 'pending',
    min_n INTEGER NOT NULL,
    max_n INTEGER NOT NULL,
    results TEXT,
    best_fit TEXT,
    best_fit_r2 REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS complexity_analyses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    source_code TEXT NOT NULL,
    input_generator TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    results TEXT,
    best_fit TEXT,
    best_fit_r2 REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);
"""


class Database:
    def __init__(self, path: Path):
        self.path = path
        self._conn: Optional[aiosqlite.Connection] = None

    async def init(self):
        self._conn = await aiosqlite.connect(self.path)
        self._conn.row_factory = aiosqlite.Row
        await self._conn.executescript(SCHEMA)
        await self._conn.commit()

    async def close(self):
        if self._conn:
            await self._conn.close()

    async def execute(self, sql: str, params: tuple = ()) -> int:
        cursor = await self._conn.execute(sql, params)
        await self._conn.commit()
        return cursor.lastrowid

    async def fetch_all(self, sql: str, params: tuple = ()) -> list:
        cursor = await self._conn.execute(sql, params)
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]

    async def fetch_one(self, sql: str, params: tuple = ()) -> Optional[dict]:
        cursor = await self._conn.execute(sql, params)
        row = await cursor.fetchone()
        return dict(row) if row else None
