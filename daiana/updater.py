import csv
from pathlib import Path
from datetime import date
from daiana.utils import rewrite_filename, check_dir_exist
from daiana.allowed import *


def load_rows_career(career_path: str) -> tuple[list[dict], Path]:
    data_dir = check_dir_exist()
    rewritten = rewrite_filename(career_path)
    csv_path = data_dir/f"{rewritten}_jobs.csv"

    if not csv_path.exists():
        raise FileNotFoundError(f"That CSV does not seem to exist at {csv_path}. Double check your typing (?)")

    with csv_path.open("r", newline="", encoding='utf-8') as f:
        rows = list(csv.DictReader(f))

    return rows, csv_path


def find_rows(rows: list[dict],
              position: str,
              company: str) -> list[tuple[int, dict]]:
    matches = []
    for i, row in enumerate(rows):
        job_pos = (row.get("job_position") or "").strip()
        comp_name = (row.get("company_name") or "").strip()

        if (
            job_pos.lower() == position.strip().lower()
            and comp_name.lower() == company.strip().lower()
        ):
            matches.append((i, row))
    return matches


def update_rows(rows: list[dict],
                row_index: int,
                new_status: str) -> None:

    today = date.today().isoformat()
    row = rows[row_index]
    old_history = row.get("history") or ""
    new_history = f"{new_status}"

    row["history"] = f"{old_history} | {new_history}: {today}" if old_history else new_history
    row["status"] = new_history


def write_rows(csv_path: Path,
               rows: list[dict]) -> None:

    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
