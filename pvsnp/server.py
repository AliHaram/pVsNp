from __future__ import annotations
import time
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from pvsnp.config import config
from pvsnp.db import Database


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.start_time = time.time()
    db = Database(config.db_path)
    await db.init()
    app.state.db = db
    app.state.algorithms_dir = config.algorithms_dir
    config.algorithms_dir.mkdir(exist_ok=True)
    yield
    await db.close()


app = FastAPI(title="P vs NP Research Workbench", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db(request: Request) -> Database:
    return request.app.state.db


from pvsnp.api import router  # noqa: E402
app.include_router(router, prefix="/api")

import os  # noqa: E402
_frontend_dist = Path(__file__).parent.parent / "frontend" / "dist"
if _frontend_dist.exists():
    from starlette.responses import FileResponse

    app.mount("/assets", StaticFiles(directory=_frontend_dist / "assets"), name="assets")

    @app.get("/{path:path}")
    async def serve_frontend(path: str):
        file_path = _frontend_dist / path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(_frontend_dist / "index.html")
