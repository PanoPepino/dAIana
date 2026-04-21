import re
import json

from pathlib import Path

from daiana.utils.constants import FIELDNAMES


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


def filter_job_dict(job: dict) -> dict:
    """
    Keep only the fields that save_job_in_csv expects.
    """
    expected = FIELDNAMES
    return {k: v for k, v in job.items() if k in expected}
