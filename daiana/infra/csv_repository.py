"""CSV persistence helpers — replaces utils/for_csv.py."""
from __future__ import annotations

import csv
import json
import re
from datetime import date
from pathlib import Path

from daiana.utils.constants import FIELDNAMES


def rewrite_filename(name: str) -> str:
    """Slugify a string for use as a filename."""
    name = name.strip().lower()
    name = re.sub(r"[^a-z0-9]+", "_", name)
    return name.strip("_") or "default"


def get_tracking_dir() -> Path:
    """Return (and create if needed) the job_tracking/ directory."""
    data_dir = Path.cwd() / "job_tracking"
    data_dir.mkdir(exist_ok=True)
    return data_dir


def csv_path_for(career: str) -> Path:
    return get_tracking_dir() / f"{rewrite_filename(career)}_jobs.csv"


def save_job(career: str, job_position: str, company_name: str,
             location: str, job_link: str) -> Path:
    when = date.today().isoformat()
    path = csv_path_for(career)
    path.parent.mkdir(parents=True, exist_ok=True)
    job_info = {
        "job_position": job_position,
        "company_name": company_name,
        "location": location,
        "history": json.dumps({"applied": when}),
        "job_link": job_link,
    }
    file_exists = path.exists()
    with path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(job_info.keys()))
        if not file_exists:
            writer.writeheader()
        writer.writerow(job_info)
    return path


def load_rows(career: str) -> tuple[list[dict], Path]:
    path = csv_path_for(career)
    if not path.exists():
        raise FileNotFoundError(f"CSV not found at {path}. Check your career name.")
    with path.open("r", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return rows, path


def write_rows(csv_path: Path, rows: list[dict]) -> None:
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def get_current_status(history_json: str) -> tuple[str, str] | None:
    if not history_json or history_json == "{}":
        return None
    try:
        history = json.loads(history_json)
        last_key = max(history.keys())
        return last_key, history[last_key]
    except (json.JSONDecodeError, KeyError, ValueError):
        return None


def filter_job_dict(job: dict) -> dict:
    return {k: v for k, v in job.items() if k in set(FIELDNAMES)}
