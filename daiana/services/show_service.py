"""Show service — replaces core/shower.py."""
from pathlib import Path

from daiana.infra.csv_repository import load_rows


def get_last_jobs(career_path: str, last_jobs: int = 20) -> tuple[list[dict], Path, int]:
    rows, csv_path = load_rows(career_path)
    total = len(rows)
    last = rows[-last_jobs:] if last_jobs > 0 else []
    return last, csv_path, total
