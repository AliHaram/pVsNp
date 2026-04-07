# tests/test_loader.py
import pytest
from pathlib import Path
from pvsnp.engine.loader import parse_metadata, load_algorithm


def test_parse_metadata():
    source = '''"""
name: My Algo
author: tester
description: A test algorithm
category: heuristic
"""

def solve(distance_matrix):
    return list(range(len(distance_matrix)))
'''
    meta = parse_metadata(source)
    assert meta["name"] == "My Algo"
    assert meta["author"] == "tester"
    assert meta["description"] == "A test algorithm"
    assert meta["category"] == "heuristic"


def test_parse_metadata_missing_fields():
    source = '''"""
name: Minimal
"""

def solve(m):
    return [0]
'''
    meta = parse_metadata(source)
    assert meta["name"] == "Minimal"
    assert meta["author"] == ""
    assert meta["description"] == ""
    assert meta["category"] == ""


def test_load_algorithm(tmp_path):
    algo_file = tmp_path / "test_algo.py"
    algo_file.write_text('''"""
name: Test
author: t
description: d
category: c
"""

def solve(distance_matrix):
    n = len(distance_matrix)
    return list(range(n))
''')
    meta, solve_fn = load_algorithm(algo_file)
    assert meta["name"] == "Test"
    result = solve_fn([[0, 1], [1, 0]])
    assert result == [0, 1]


def test_load_algorithm_no_solve_raises(tmp_path):
    algo_file = tmp_path / "bad.py"
    algo_file.write_text('x = 1\n')
    with pytest.raises(ValueError, match="No 'solve' function"):
        load_algorithm(algo_file)
