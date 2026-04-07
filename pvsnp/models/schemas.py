# pvsnp/models/schemas.py
from __future__ import annotations
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


# --- Algorithms ---

class AlgorithmOut(BaseModel):
    id: int
    name: str
    author: str
    description: str
    category: str
    filename: str
    created_at: str


# --- Instances ---

class InstanceGenerateRequest(BaseModel):
    instance_type: str  # random, clustered, grid, adversarial
    n: int
    count: int = 1
    name: str = ""


class InstanceOut(BaseModel):
    id: int
    name: str
    instance_type: str
    n: int
    points: List[List[float]]
    distance_matrix: List[List[float]]
    created_at: str


class InstanceSummary(BaseModel):
    id: int
    name: str
    instance_type: str
    n: int
    created_at: str


# --- Benchmarks ---

class BenchmarkRunRequest(BaseModel):
    algorithm_ids: List[int]
    instance_ids: List[int]


class BenchmarkResultOut(BaseModel):
    id: int
    run_id: int
    algorithm_id: int
    algorithm_name: str
    instance_id: int
    tour: Optional[List[int]]
    tour_length: Optional[float]
    is_optimal: Optional[bool]
    execution_time: Optional[float]
    error: Optional[str]


class BenchmarkRunOut(BaseModel):
    id: int
    status: str
    results: List[BenchmarkResultOut]
    created_at: str
    completed_at: Optional[str]


# --- Counterexamples ---

class CounterexampleHuntRequest(BaseModel):
    algorithm_id: int
    strategy: str = "random"  # random, structured, mutation
    count: int = 100
    max_n: int = 12


class CounterexampleOut(BaseModel):
    id: int
    algorithm_id: int
    instance_id: int
    algorithm_tour: List[int]
    algorithm_tour_length: float
    optimal_tour: List[int]
    optimal_tour_length: float
    created_at: str


# --- Profiler ---

class ProfilerRunRequest(BaseModel):
    algorithm_id: int
    min_n: int = 5
    max_n: int = 200
    samples_per_size: int = 3


class CurveFitResult(BaseModel):
    name: str  # e.g. "O(n²)"
    r_squared: float


class ProfilerDataPoint(BaseModel):
    n: int
    time: float


class ProfilerRunOut(BaseModel):
    id: int
    algorithm_id: int
    status: str
    min_n: int
    max_n: int
    data_points: List[ProfilerDataPoint]
    fits: List[CurveFitResult]
    best_fit: Optional[str]
    best_fit_r2: Optional[float]
    created_at: str
    completed_at: Optional[str]


# --- Complexity Finder ---

class ComplexityAnalyzeRequest(BaseModel):
    input_generator: str = "random_list"


class ComplexityAnalysisOut(BaseModel):
    id: int
    name: str
    status: str
    input_generator: str
    data_points: List[ProfilerDataPoint]
    fits: List[CurveFitResult]
    best_fit: Optional[str]
    best_fit_r2: Optional[float]
    created_at: str
    completed_at: Optional[str]


# --- Status ---

class StatusOut(BaseModel):
    workers_active: int
    workers_total: int
    algorithms_count: int
    instances_count: int
    db_size_bytes: int
    uptime_seconds: float
