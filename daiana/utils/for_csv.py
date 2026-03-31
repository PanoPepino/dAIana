import re
from pathlib import Path
import click
import json

from daiana.utils.constants import FIELDNAMES
from daiana.utils.styles import *


def rewrite_filename(name: str) -> str:
    """
    Function to replace spaces and the line with underscore, so it is properly understood.

    Args:
        name (str): Whatever str.

    Returns:
        str: Replace str.
    """

    name = name.strip().lower()
    # Replace any sequence of non-alphanumeric characters with underscore
    name = re.sub(r"[^a-z0-9]+", "_", name)

    # Remove leading/trailing underscores
    name = name.strip("_")
    return name or "default"


def check_dir_exist() -> Path:
    """
    This function checks if a given folder exists. If not, creates it.

    Returns:
        Path: the current direction / job_tracking.
    """

    original_dir = Path.cwd()
    data_dir = original_dir/'job_tracking'
    data_dir.mkdir(exist_ok=True)
    return data_dir


def get_current_status(history_json: str) -> str:
    """
    Simple function to get the last status of the history, to be displayed when :func:`update` is used.

    Args:
        history_json (str): The whole history of status changes in json.

    Returns:
        str: The status of the last update colored in its associated color.
    """

    if not history_json or history_json == "{}":
        return ""
    try:
        history = json.loads(history_json)
        last_key = max(history.keys())
        return last_key, history[last_key]

    except (json.JSONDecodeError, KeyError, ValueError):
        # Fallback for old string format
        return print("Seems your history is not a json object...")


def history_format_display(history_json: str,
                           latest_only: bool = True) -> str:
    """
    This function eats the history status for all the job positions and splits it in such a way that it only show the update dates in the given color of a status.

    Args:
        history (str): The entry of a job position that contains all the status update.

    Returns:
        str: The entry only with the dates colored in the associated status.
    """

    action, latest_update = get_current_status(history_json)

    if not action:
        return click.style('-', fg='red')

    # Getting color

    color_style = get_status_color(action)

    if latest_only:
        return click.style(latest_update, **color_style)

    # Full history display with the right colors

    try:
        history = json.loads(history_json)
        items = []
        for key in sorted(history.keys()):
            update_day = history[key]
            items.append(click.style(update_day, **get_status_color(key)))

        return click.style(" ".join(items), **color_style)

    except:
        pass


def filter_job_dict(job: dict) -> dict:
    """
    Keep only the fields that save_job_in_csv expects.
    """
    expected = FIELDNAMES
    return {k: v for k, v in job.items() if k in expected}
