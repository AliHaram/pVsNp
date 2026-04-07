# P vs NP Research Workbench — Design Spec

**Project:** pVsNp
**Date:** 2026-04-07
**Watermark:** Connected

## Overview

A web-based research workbench for exploring novel approaches to the Travelling Salesman Problem and the P vs NP question. Designed to be used by humans and AI agents alike — submit algorithms, test them against exact solutions, hunt for counterexamples, and measure empirical complexity. Built for open-source collaboration on GitHub.

The workbench ships with baseline algorithms (brute force, nearest neighbor, Christofides, 2-opt) and provides tooling to rigorously test any new approach: verify correctness, profile scaling behavior, and aggressively search for counterexamples.

## Architecture

**Monolith + Worker** — a single FastAPI server handles the REST API, coordinates tasks, and serves the React frontend. Algorithm execution happens in isolated subprocess workers with configurable timeout (default 60s) and memory limits. The server stays responsive even if an algorithm hangs or crashes.

**Storage:** SQLite — zero config, single file, easy to share/backup. Stores algorithms, instances, benchmark runs, results, and counterexamples.

**Live updates:** WebSocket endpoint for real-time progress as algorithms run — no polling.

### System Components

```
┌─────────────────────────┐         ┌──────────────────────────────────┐
│   React Frontend        │  REST   │   FastAPI Server                 │
│   (Vite + TypeScript)   │◄──────►│   API Gateway + Task Coordinator │
│                         │  + WSS  │                                  │
│  - Graph Viewer (D3.js) │         │  ┌─────────┐  ┌──────────────┐  │
│  - Scaling Charts       │         │  │ REST API │  │  Services    │  │
│  - Algorithm Editor     │         │  │          │  │  Instance Gen│  │
│  - Results Dashboard    │         │  │          │  │  Verification│  │
│                         │         │  │          │  │  Curve Fit   │  │
│                         │         │  │          │  │  Counter Ex  │  │
│                         │         │  └─────────┘  └──────────────┘  │
│                         │         │                                  │
│                         │         │  ┌────────────────────────────┐  │
│                         │         │  │ Worker Pool (subprocesses) │  │
│                         │         │  │  W1  W2  W3  W4           │  │
│                         │         │  │  Isolated · Timeout · Mem  │  │
│                         │         │  └────────────────────────────┘  │
│                         │         │                                  │
│                         │         │  ┌────────────────────────────┐  │
│                         │         │  │ SQLite                     │  │
│                         │         │  │ Algos·Instances·Results    │  │
│                         │         │  └────────────────────────────┘  │
└─────────────────────────┘         └──────────────────────────────────┘
```

## Tech Stack

- **Backend:** Python 3.11+, FastAPI, SQLite (aiosqlite), subprocess worker pool
- **Frontend:** React 18+, TypeScript, Vite, D3.js (graph visualization), Recharts (scaling charts)
- **Monospace font:** JetBrains Mono throughout

## Algorithm Plugin Interface

Algorithms are Python files with a single `solve` function and metadata in a docstring header:

```python
"""
name: My Novel Approach
author: johndoe
description: Geometric decomposition via convex layers
category: geometric
"""

def solve(distance_matrix: list[list[float]]) -> list[int]:
    """
    Input: NxN distance matrix
    Output: Tour as list of node indices [0, 3, 1, 2, ...]
    Must visit every node exactly once.
    """
    n = len(distance_matrix)
    tour = my_algorithm(distance_matrix)
    return tour
```

Algorithms are placed in the `algorithms/` directory or uploaded via the REST API / web UI.

### Complexity Finder Interface

For general-purpose complexity analysis (not TSP-specific), algorithms use a `run` function:

```python
"""
name: Merge Sort
input_generator: random_list
"""

def run(data: list) -> list:
    if len(data) <= 1:
        return data
    mid = len(data) // 2
    return merge(run(data[:mid]), run(data[mid:]))
```

Supported input generators: `random_list`, `sorted_list`, `reversed_list`, `random_graph`, `random_string`, `custom`.

## V1 Modules

### Module 1: Algorithm Arena

- Submit algorithms via UI upload or file drop into `algorithms/`
- Run against configurable instance sets
- Side-by-side comparison of multiple algorithms
- Leaderboard: correctness rate, average tour quality, scaling behavior
- Ships with baselines: brute force, nearest neighbor, Christofides, 2-opt

### Module 2: Instance Generator

- **Random uniform** — points in 2D plane
- **Clustered** — grouped point clouds
- **Grid** — structured lattice arrangements
- **Adversarial** — designed to break greedy heuristics
- **Custom** — upload or draw points in the UI

### Module 3: Counterexample Engine

- For each algorithm, systematically hunt for inputs where it produces suboptimal tours
- Compare against exact solution via brute force (n ≤ 20)
- Strategies: random, structured, mutation of known failures
- Store all counterexamples in a searchable database
- Stress test mode: run thousands of instances automatically

### Module 4: Complexity Profiler (TSP-specific)

- Run algorithm across instance sizes (n=5 to n=500+)
- Measure wall time, memory usage, operations count
- Curve fitting: determine if scaling is O(n²), O(n³), O(2^n), etc.
- Visual scaling chart with polynomial vs exponential overlay
- Alert when scaling appears exponential despite passing small tests

### Module 5: Complexity Finder (General Purpose)

- Analyze any algorithm, not just TSP solvers
- Generate inputs at 48 logarithmically-spaced sizes (n=10 to n=100,000)
- Run 5x per size, take median to reduce noise
- Track wall time and peak memory
- Fit against known complexity classes: O(1), O(log n), O(n), O(n log n), O(n²), O(n³), O(2^n)
- Rank by R² goodness-of-fit and report confidence percentage
- Test best/average/worst case separately using different input generators

## Frontend Design

### Visual Identity

- **Theme:** Subtle retro — dark background (#0a0a0f), terminal green primary (#6ee7b7), monospace everywhere
- **Retro touches:** Faint scanline overlay, soft glow on primary text, blinking cursor on status indicators, 1px solid borders, no drop shadows, no gradients
- **Typography:** JetBrains Mono for all text. The whole app feels like a terminal that grew a UI.
- **Branding:** "Connected" watermark in top nav and footer

### Color Palette

| Role | Color | Hex |
|------|-------|-----|
| Background | Near black | #0a0a0f |
| Primary | Terminal green | #6ee7b7 |
| Secondary | Soft indigo | #a5b4fc |
| Accent/Warning | Amber | #fbbf24 |
| Danger | Soft red | #fca5a5 |
| Muted text | Slate | #475569 |

### Layout

- **Top nav:** `P vs NP │ Arena · Instances · Counterexamples · Profiler · Complexity Finder` — "Connected" right-aligned
- **Main view:** Split-panel — graph visualization left, results/data right
- **Bottom status bar:** Worker status, instance count, DB size, uptime
- **Results:** Monospace tables, not cards or material design

### Key Pages

- **Arena** — algorithm list, submit new, run benchmarks, leaderboard
- **Instances** — generate, browse, draw custom points in graph viewer
- **Counterexamples** — browse failures, filter by algorithm, replay on graph
- **Profiler** — scaling charts with polynomial/exponential curve fits overlaid
- **Complexity Finder** — upload any algorithm, see classification + curve fits + confidence

## REST API

### Algorithms
- `GET /api/algorithms` — list all registered algorithms
- `POST /api/algorithms` — upload a new algorithm (.py file)
- `GET /api/algorithms/{id}` — get algorithm details + stats
- `DELETE /api/algorithms/{id}` — remove an algorithm

### Instances
- `POST /api/instances/generate` — generate TSP instances `{type, n, count}`
- `GET /api/instances` — list stored instances
- `GET /api/instances/{id}` — get instance data (points, distance matrix)

### Benchmarks
- `POST /api/benchmarks/run` — run algorithm(s) against instance(s)
- `GET /api/benchmarks/{id}` — get benchmark results
- `GET /api/benchmarks` — list all benchmark runs

### Counterexamples
- `POST /api/counterexamples/hunt` — start hunting for failures `{algorithm_id, strategy, count}`
- `GET /api/counterexamples` — list found counterexamples

### Profiler
- `POST /api/profiler/run` — profile algorithm scaling `{algorithm_id, min_n, max_n}`
- `GET /api/profiler/{id}` — get profiling results + curve fits

### Complexity Finder
- `POST /api/complexity/analyze` — upload & analyze any algorithm `{file, input_gen}`
- `GET /api/complexity/{id}` — get analysis results

### Live Updates
- `WSS /api/ws` — real-time progress for running tasks

All long-running operations return a task ID. Progress is streamed via WebSocket.

## Project Structure

```
pVsNp/
├── pvsnp/                    # Backend package
│   ├── __main__.py           # Entry point
│   ├── server.py             # FastAPI app
│   ├── config.py             # Settings
│   ├── db.py                 # SQLite setup
│   ├── worker.py             # Subprocess pool
│   ├── api/
│   │   ├── algorithms.py     # CRUD + upload
│   │   ├── instances.py      # Generation
│   │   ├── benchmarks.py     # Run + results
│   │   ├── counterexamples.py
│   │   ├── profiler.py
│   │   ├── complexity.py     # General finder
│   │   └── ws.py             # WebSocket
│   ├── engine/
│   │   ├── runner.py         # Execute algorithm in subprocess
│   │   ├── verifier.py       # Check tour validity + optimality
│   │   ├── generator.py      # TSP instance generation
│   │   ├── curve_fitter.py   # Complexity curve fitting
│   │   └── counterexample.py # Counterexample search strategies
│   ├── models/               # Pydantic schemas
│   └── algorithms/           # Built-in baselines
│       ├── brute_force.py
│       ├── nearest_neighbor.py
│       ├── christofides.py
│       └── two_opt.py
├── frontend/                 # React app
│   ├── index.html
│   ├── vite.config.ts
│   ├── src/
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   ├── api/
│   │   │   └── client.ts     # API + WS client
│   │   ├── components/
│   │   │   ├── GraphViewer.tsx    # D3 graph visualization
│   │   │   ├── ScalingChart.tsx   # Recharts scaling plots
│   │   │   ├── CodeEditor.tsx     # Algorithm input
│   │   │   ├── ResultsTable.tsx
│   │   │   └── StatusBar.tsx
│   │   ├── pages/
│   │   │   ├── Arena.tsx
│   │   │   ├── Instances.tsx
│   │   │   ├── Counterexamples.tsx
│   │   │   ├── Profiler.tsx
│   │   │   └── ComplexityFinder.tsx
│   │   └── theme/
│   │       └── retro.css     # Retro theme styles
│   ├── public/
│   └── package.json
├── algorithms/               # User-submitted algorithms
├── tests/                    # pytest suite
├── README.md                 # Setup + security disclaimer
├── pyproject.toml            # Python deps + config
└── .gitignore
```

## README Security Disclaimer

The README must include a prominent disclaimer:

> **Security Notice:** This workbench executes algorithm code locally on your machine. Submitted algorithms run as subprocesses with timeout and memory limits, but are **not sandboxed** from your filesystem. Only run algorithms you trust. Do not run untrusted code from unknown sources without reviewing it first.

## Scope Boundaries

### V1 (this spec)
- Algorithm Arena, Instance Generator, Counterexample Engine, Complexity Profiler, Complexity Finder
- Web UI with retro theme, graph visualization, live results
- REST API for agent/programmatic access
- WebSocket for live progress
- Built-in baseline algorithms

### V2 (future)
- Pattern Observatory — bulk analysis of solved instances, ML-powered pattern detection
- Conjecture Lab — formalize and track hypotheses

### V3 (future)
- Proof Sketch Workspace
- AI-driven autonomous experimentation loops
