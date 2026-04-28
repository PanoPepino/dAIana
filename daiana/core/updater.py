"""Compatibility shim — use daiana.services.update_service instead."""
from daiana.services.update_service import (
    load_rows_career,
    find_rows,
    update_history,
    edit_entry,
    select_matching_row,
)
from daiana.infra.csv_repository import write_rows

__all__ = [
    "load_rows_career",
    "find_rows",
    "update_history",
    "edit_entry",
    "select_matching_row",
    "write_rows",
]
