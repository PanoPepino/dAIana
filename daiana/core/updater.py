import csv
from pathlib import Path
from datetime import date
import json

from daiana.utils.for_csv import rewrite_filename, check_dir_exist
from daiana.utils.constants import *


def load_rows_career(career: str) -> tuple[list[dict], Path]:
    """
    Simple function to load .csv data given a path.

    Args:
        career (str): The path.

    Raises:
        FileNotFoundError: In case you misspeled your path, this error will be raised.,

    Returns:
        tuple[list[dict], Path]: The .csv read and the path.
    """
    data_dir = check_dir_exist()
    rewritten = rewrite_filename(career)
    csv_path = data_dir/f"{rewritten}_jobs.csv"

    if not csv_path.exists():
        raise FileNotFoundError(f"That CSV does not seem to exist at {csv_path}. Double check your typing (?)")

    with csv_path.open("r", newline="", encoding='utf-8') as f:
        rows = list(csv.DictReader(f))

    return rows, csv_path


def find_rows(rows: list[dict],
              position: str,
              company: str) -> list[tuple[int, dict]]:
    """
    Given a load dictionary, it will find the row that contain a given position in a given company.

    Args:
        rows (list[dict]): The load csv.
        position (str): The postion you are looking for.
        company (str): The company that offers such position.

    Returns:
        list[tuple[int, dict]]: A set of matches (in case you have applied to similar positions in the same company)
    """
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
    """
    Given the chosen rows in previous :func:`find_rows`, it will allow you to update the history status of the job position.

    Args:
        rows (list[dict]): The chosen rows.
        row_index (int): The position of your desired job, in case it repeats for some reason.
        new_status (str): Just the status of the job. This will be added as new_status:date in the history json.
    """

    today = date.today().isoformat()
    row = rows[row_index]

    # Reading old history
    old_history = row.get("history", "{}")
    try:
        history = json.loads(old_history) if old_history else {}
    except:
        pass

    # Appending new history
    history[new_status] = today
    row['history'] = json.dumps(history)


def write_rows(csv_path: Path,
               rows: list[dict]) -> None:
    """
    This is just to write any changes you have performed in your database.
    """

    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
