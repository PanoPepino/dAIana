"""Update service — replaces core/updater.py."""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from daiana.infra.csv_repository import load_rows, write_rows
from daiana.utils.constants import FIELDNAMES


def load_rows_career(career: str) -> tuple[list[dict], Path]:
    return load_rows(career)


def find_rows(rows: list[dict], position: str, company: str) -> list[tuple[int, dict]]:
    matches = []
    for i, row in enumerate(rows):
        jp = (row.get("job_position") or "").strip().lower()
        cn = (row.get("company_name") or "").strip().lower()
        if jp == position.strip().lower() and cn == company.strip().lower():
            matches.append((i, row))
    return matches


def update_history(rows: list[dict], row_index: int, new_status: str) -> None:
    today = date.today().isoformat()
    row = rows[row_index]
    old = row.get("history", "{}")
    try:
        history = json.loads(old) if old else {}
    except Exception:
        history = {}
    history[new_status] = today
    row["history"] = json.dumps(history)


def edit_entry(rows: list[dict], row_index: int, to_edit: str, new_entry: str) -> None:
    rows[row_index][to_edit.lower()] = new_entry


def select_matching_row(rows: list[dict], position: str, company: str) -> tuple[int, dict] | list | None:
    matches = find_rows(rows, position, company)
    if not matches:
        return None
    if len(matches) == 1:
        return matches[0]
    return matches
