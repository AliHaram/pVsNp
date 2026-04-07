from __future__ import annotations
from fastapi import APIRouter
from pvsnp.api.algorithms import router as algorithms_router
from pvsnp.api.instances import router as instances_router
from pvsnp.api.benchmarks import router as benchmarks_router
from pvsnp.api.counterexamples import router as counterexamples_router
from pvsnp.api.profiler import router as profiler_router
from pvsnp.api.complexity import router as complexity_router
from pvsnp.api.ws import router as ws_router
from pvsnp.api.status import router as status_router

router = APIRouter()
router.include_router(algorithms_router, prefix="/algorithms", tags=["algorithms"])
router.include_router(instances_router, prefix="/instances", tags=["instances"])
router.include_router(benchmarks_router, prefix="/benchmarks", tags=["benchmarks"])
router.include_router(counterexamples_router, prefix="/counterexamples", tags=["counterexamples"])
router.include_router(profiler_router, prefix="/profiler", tags=["profiler"])
router.include_router(complexity_router, prefix="/complexity", tags=["complexity"])
router.include_router(ws_router, tags=["websocket"])
router.include_router(status_router, tags=["status"])
