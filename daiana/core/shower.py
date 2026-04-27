"""
This file contains super simple information to display on terminal your n latest saved jobs for a given career path.
"""

import csv

from collections import deque

from daiana.utils.for_csv import rewrite_filename, check_dir_exist


import csv
from pathlib import Path


def get_last_jobs(
    career_path: str,
    last_jobs: int = 20,
) -> tuple[list[dict], Path, float]:
    """
    Read the desired career CSV and return the last `last_jobs` rows,
    the CSV path, and the total number of rows in the file.

    Args:
        career_path (str): Career path to inspect.
        last_jobs (int, optional): How many recent jobs to return. Defaults to 20.

    Raises:
        FileNotFoundError: If the CSV file does not exist.

    Returns:
        tuple[list[dict], Path, float]:
            - The last `last_jobs` rows
            - The CSV path
            - The total number of rows as a float
    """
    data_dir = check_dir_exist()
    rewritten = rewrite_filename(career_path)
    csv_path = data_dir / f"{rewritten}_jobs.csv"

    if not csv_path.exists():
        raise FileNotFoundError(
            f"That CSV does not seem to exist at {csv_path}. Double check your typing (?)"
        )

    with csv_path.open("r", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    total_rows = int(len(rows))
    last_rows = rows[-last_jobs:] if last_jobs > 0 else []

    return last_rows, csv_path, total_rows
