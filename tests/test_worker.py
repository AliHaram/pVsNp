# tests/test_worker.py
import pytest
import asyncio
from pvsnp.worker import run_algorithm_subprocess


@pytest.mark.asyncio
async def test_run_algorithm_success():
    code = '''
def solve(distance_matrix):
    n = len(distance_matrix)
    return list(range(n))
'''
    matrix = [[0, 1, 2], [1, 0, 1], [2, 1, 0]]
    result = await run_algorithm_subprocess(code, matrix, timeout=10)
    assert result["status"] == "success"
    assert result["tour"] == [0, 1, 2]
    assert result["execution_time"] > 0


@pytest.mark.asyncio
async def test_run_algorithm_timeout():
    code = '''
import time
def solve(distance_matrix):
    time.sleep(100)
    return [0]
'''
    matrix = [[0, 1], [1, 0]]
    result = await run_algorithm_subprocess(code, matrix, timeout=1)
    assert result["status"] == "error"
    assert "timeout" in result["error"].lower()


@pytest.mark.asyncio
async def test_run_algorithm_runtime_error():
    code = '''
def solve(distance_matrix):
    raise ValueError("broken")
'''
    matrix = [[0, 1], [1, 0]]
    result = await run_algorithm_subprocess(code, matrix, timeout=10)
    assert result["status"] == "error"
    assert "broken" in result["error"]


@pytest.mark.asyncio
async def test_run_algorithm_syntax_error():
    code = 'def solve(m):\n  return [[[['
    matrix = [[0, 1], [1, 0]]
    result = await run_algorithm_subprocess(code, matrix, timeout=10)
    assert result["status"] == "error"
