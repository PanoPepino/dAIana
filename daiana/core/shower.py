"""
This file contains super simple information to display on terminal your n latest saved jobs for a given career path.
"""

import csv

from collections import deque

from daiana.utils.for_csv import rewrite_filename, check_dir_exist


def get_last_jobs(career_path: str,
                  last_jobs: int = 20) -> list[dict]:
    """
    This function will read your desired `career_path` .csv and then extract `last_jobs` rows to be displayed.

    Args:
        career_path (str): the career path that you wanna inspect.
        last_jobs (int, optional): How many jobs to inspect. Defaults to 15.

    Raises:
        FileNotFoundError: In case you misstype the career_path.

    Returns:
        list[dict]: The `last_jobs` rows of such document.
    """

    data_dir = check_dir_exist()
    rewritten = rewrite_filename(career_path)
    csv_path = data_dir/f"{rewritten}_jobs.csv"

    if not csv_path.exists():
        raise FileNotFoundError(f"That CSV does not seem to exist at {csv_path}. Double check your typing (?)")

    with csv_path.open("r", newline="", encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = deque(reader, maxlen=last_jobs)

    return list(rows), csv_path
