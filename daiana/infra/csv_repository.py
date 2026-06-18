"""CSV persistence helpers — replaces utils/for_csv.py."""
from __future__ import annotations

import csv
import json
import re
from datetime import date
from pathlib import Path

from daiana.utils.constants import FIELDNAMES, CONTACT_FIELDNAMES


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
    """Resolve the jobs CSV path for a given career slug."""
    return get_tracking_dir() / f"{rewrite_filename(career)}_jobs.csv"


# ── Contacts: fixed global path ───────────────────────────────────────────────

def contacts_csv_path() -> Path:
    """
    Return the fixed path for the global contacts table.
    Contacts are career-agnostic — always stored at job_tracking/contacts.csv.
    """
    return get_tracking_dir() / "contacts.csv"


def save_contact(contact_name: str, company: str, location: str,
                 email: str, date_of_contact: str) -> Path:
    """
    Append a new contact row to contacts.csv.
    Creates the file with headers if it does not exist yet.
    """
    path = contacts_csv_path()
    contact_info = {
        "contact_name": contact_name,
        "company": company,
        "location": location,
        "email": email,
        "date_of_contact": date_of_contact,
    }
    file_exists = path.exists()
    with path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CONTACT_FIELDNAMES)
        # Write header only once, when the file is first created
        if not file_exists:
            writer.writeheader()
        writer.writerow(contact_info)
    return path


def load_contacts() -> tuple[list[dict], Path]:
    """
    Load all rows from contacts.csv.
    Raises FileNotFoundError if no contacts have been saved yet.
    """
    path = contacts_csv_path()
    if not path.exists():
        raise FileNotFoundError(
            f"No contacts file found at {path}. "
            "Save a contact first with: daiana contacts save"
        )
    with path.open("r", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return rows, path


def write_contacts(rows: list[dict]) -> None:
    """
    Overwrite contacts.csv with the given list of rows.
    Used by the update/erase flow after in-memory modifications.
    """
    path = contacts_csv_path()
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CONTACT_FIELDNAMES, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


# ── Jobs (unchanged) ──────────────────────────────────────────────────────────

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
