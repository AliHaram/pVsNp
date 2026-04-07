# pvsnp/engine/loader.py
from __future__ import annotations
import importlib.util
import re
from pathlib import Path
from typing import Callable, Dict, Tuple


def parse_metadata(source: str) -> Dict[str, str]:
    match = re.match(r'^"""(.*?)"""', source, re.DOTALL)
    if not match:
        match = re.match(r"^'''(.*?)'''", source, re.DOTALL)
    meta = {"name": "", "author": "", "description": "", "category": ""}
    if match:
        for line in match.group(1).strip().splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
                key = key.strip().lower()
                if key in meta:
                    meta[key] = value.strip()
    return meta


def load_algorithm(path: Path) -> Tuple[Dict[str, str], Callable]:
    source = path.read_text()
    meta = parse_metadata(source)
    if not meta["name"]:
        meta["name"] = path.stem

    spec = importlib.util.spec_from_file_location(f"algo_{path.stem}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    if not hasattr(module, "solve"):
        raise ValueError(f"No 'solve' function found in {path}")

    return meta, module.solve
