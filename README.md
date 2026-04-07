# P vs NP Research Workbench

A web-based research workbench for exploring novel approaches to the Travelling Salesman Problem and the P vs NP question. Submit algorithms, verify correctness against exact solutions, hunt for counterexamples, and measure empirical complexity.

Designed for humans and AI agents alike.

> **Security Notice:** This workbench executes algorithm code locally on your machine. Submitted algorithms run as subprocesses with timeout and memory limits, but are **not sandboxed** from your filesystem. Only run algorithms you trust. Do not run untrusted code from unknown sources without reviewing it first.

## Quick Start

### Backend

```bash
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -e ".[dev]"
python -m pvsnp
```

Server starts at `http://127.0.0.1:8000`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend starts at `http://localhost:5173` with API proxied to the backend.

## Modules

### Algorithm Arena
Submit TSP solver algorithms and benchmark them against each other. Ships with four baselines: brute force (exact), nearest neighbor, 2-opt, and Christofides.

### Instance Generator
Generate TSP instances of various types: random uniform, clustered, grid, and adversarial. Visualize them interactively.

### Counterexample Engine
Aggressively hunt for inputs where an algorithm produces suboptimal tours. If your algorithm survives thousands of tests, that's interesting.

### Complexity Profiler
Profile how your TSP solver scales with instance size. Fits empirical timing data to known complexity classes and tells you whether you're polynomial or exponential.

### Complexity Finder
Analyze the time complexity of any algorithm — not just TSP solvers. Upload code, select an input generator, and get an empirical complexity classification.

## Writing an Algorithm

Create a Python file with a `solve` function:

```python
"""
name: My Novel Approach
author: yourname
description: What this does
category: heuristic
"""

def solve(distance_matrix: list[list[float]]) -> list[int]:
    n = len(distance_matrix)
    # Your algorithm here
    return tour  # list of node indices, visiting each exactly once
```

Drop it in the `algorithms/` directory or upload through the web UI.

### Complexity Finder Algorithms

For the complexity finder, use a `run` function instead:

```python
"""
name: My Sort
input_generator: random_list
"""

def run(data: list) -> list:
    return sorted(data)
```

## REST API

All endpoints are under `/api`. See the running server at `/docs` for full OpenAPI documentation.

## Tech Stack

- **Backend:** Python, FastAPI, SQLite, subprocess workers
- **Frontend:** React, TypeScript, D3.js, Recharts
- **Theme:** Retro terminal aesthetic

---

*Connected*
