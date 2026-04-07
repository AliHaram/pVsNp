# pvsnp/worker.py
from __future__ import annotations
import asyncio
import json
import sys
import textwrap
import time


_WORKER_SCRIPT = textwrap.dedent("""\
    import json
    import sys
    import time

    def main():
        data = json.loads(sys.stdin.read())
        code = data["code"]
        matrix = data["matrix"]

        namespace = {}
        try:
            exec(code, namespace)
        except Exception as e:
            print(json.dumps({"status": "error", "error": f"Compilation error: {e}"}))
            return

        solve = namespace.get("solve")
        if solve is None:
            # Check for 'run' (complexity finder interface)
            solve = namespace.get("run")
        if solve is None:
            print(json.dumps({"status": "error", "error": "No 'solve' or 'run' function found"}))
            return

        try:
            start = time.perf_counter()
            result = solve(matrix)
            elapsed = time.perf_counter() - start
            print(json.dumps({
                "status": "success",
                "tour": result,
                "execution_time": elapsed,
            }))
        except Exception as e:
            print(json.dumps({"status": "error", "error": str(e)}))

    main()
""")


async def run_algorithm_subprocess(
    code: str,
    input_data: list,
    timeout: int = 60,
) -> dict:
    payload = json.dumps({"code": code, "matrix": input_data})
    try:
        proc = await asyncio.create_subprocess_exec(
            sys.executable, "-c", _WORKER_SCRIPT,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(
            proc.communicate(payload.encode()), timeout=timeout
        )
        if proc.returncode != 0:
            err = stderr.decode().strip() or "Process exited with non-zero status"
            return {"status": "error", "error": err, "execution_time": 0}
        return json.loads(stdout.decode())
    except asyncio.TimeoutError:
        proc.kill()
        await proc.wait()
        return {"status": "error", "error": "Timeout exceeded", "execution_time": timeout}
    except Exception as e:
        return {"status": "error", "error": str(e), "execution_time": 0}
