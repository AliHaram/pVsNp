from pathlib import Path
from dataclasses import dataclass


@dataclass
class Config:
    db_path: Path = Path("pvsnp.db")
    algorithms_dir: Path = Path("algorithms")
    builtin_algorithms_dir: Path = Path(__file__).parent / "algorithms"
    worker_count: int = 4
    default_timeout: int = 60
    max_memory_mb: int = 512
    host: str = "127.0.0.1"
    port: int = 8000


config = Config()
