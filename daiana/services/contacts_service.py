"""Contacts service — business logic for the network contacts tracker."""
from __future__ import annotations

from pathlib import Path

from daiana.infra.csv_repository import (
    save_contact,
    load_contacts,
    write_contacts,
    contacts_csv_path,
)


def save_contact_entry(
    contact_name: str,
    company: str,
    location: str,
    email: str,
    date_of_contact: str,
) -> Path:
    """
    Persist a new contact row and return the path to contacts.csv.
    All validation of inputs happens at the command layer before calling this.
    """
    return save_contact(
        contact_name=contact_name,
        company=company,
        location=location,
        email=email,
        date_of_contact=date_of_contact,
    )


def get_last_contacts(last_n: int = 20) -> tuple[list[dict], Path, int]:
    """
    Load contacts from CSV, returning:
      - the last `last_n` rows (for display)
      - the path to the CSV
      - the total number of contacts stored
    """
    rows, csv_path = load_contacts()
    total = len(rows)
    # Slice from the end so most-recent contacts appear last in the table
    last = rows[-last_n:] if last_n > 0 else []
    return last, csv_path, total


def find_contacts(rows: list[dict], name: str, company: str) -> list[tuple[int, dict]]:
    """
    Search contacts by name + company (case-insensitive exact match).
    Returns a list of (row_index, row_dict) tuples — may be empty or plural.
    """
    matches = []
    for i, row in enumerate(rows):
        stored_name    = (row.get("contact_name") or "").strip().lower()
        stored_company = (row.get("company")      or "").strip().lower()
        if stored_name == name.strip().lower() and stored_company == company.strip().lower():
            matches.append((i, row))
    return matches


def update_contact_field(
    rows: list[dict],
    row_index: int,
    field: str,
    new_value: str,
) -> None:
    """
    In-place update of a single field on the selected contact row.
    Call write_contacts() after this to persist the change.
    """
    rows[row_index][field.lower()] = new_value


def erase_contact(rows: list[dict], row_index: int) -> None:
    """
    Remove the contact at row_index from the in-memory list.
    Call write_contacts() after this to persist the deletion.
    """
    rows.pop(row_index)
