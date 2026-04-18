from __future__ import annotations

import typer
from rich.console import Console
from rich.text import Text

from daiana.core.updater import (
    edit_entry,
    find_rows,
    load_rows_career,
    update_history,
    write_rows,
)
from daiana.utils.constants import ALLOW_STATUS, FIELDNAMES
from daiana.utils.styles import history_format_rich
from daiana.utils.ui import COMMAND_COLORS, STATUS_COLORS, rgb

console = Console()

UPDATE = COMMAND_COLORS['update']
SAVE = COMMAND_COLORS['save']

EDITABLE_FIELDS = [field for field in FIELDNAMES if field != "history"]


def run_update_flow(career: str, status: bool, field: bool, erase: bool) -> None:
    _validate_mode(status, field, erase)
    console.print()

    position, company = _prompt_job_identity()

    try:
        rows, csv_path = load_rows_career(career)
    except FileNotFoundError as exc:
        console.print(f"[bold red]{exc}[/bold red]")
        raise typer.Exit(code=1)

    matches = find_rows(rows, position, company)
    if not matches:
        console.print(f"[bold {rgb(UPDATE)}]No matching job found with those fields.[/bold {rgb(UPDATE)}]")
        raise typer.Exit(code=1)

    row_index, chosen_row = _pick_matching_row(matches)
    _show_selected_job(chosen_row)

    if status:
        _handle_status_update(rows, row_index, chosen_row, csv_path)
    elif field:
        _handle_field_update(rows, row_index, csv_path)
    elif erase:
        _handle_erase(rows, row_index, chosen_row, csv_path)

    console.print()


def _validate_mode(status: bool, field: bool, erase: bool) -> None:
    selected = sum([status, field, erase])

    if selected > 1:
        console.print("[bold red]Choose only one mode: --status, --field, or --erase[/bold red]")
        raise typer.Exit(code=1)

    if selected == 0:
        console.print("[bold red]Choose one mode: --status, --field, or --erase[/bold red]")
        raise typer.Exit(code=1)


def _prompt_job_identity() -> tuple[str, str]:
    console.print(f"[bold {rgb(UPDATE)}]Fill in fields below:[/bold {rgb(UPDATE)}]")
    console.print()

    position = typer.prompt("1) Job Position").strip()
    company = typer.prompt("2) Company Name").strip()
    return position, company


def _pick_matching_row(matches: list[tuple[int, dict]]) -> tuple[int, dict]:
    if len(matches) == 1:
        return matches[0]

    console.print()
    console.print(Text(f"Found {len(matches)} matching jobs:", style=f"bold {rgb(UPDATE)}"))
    console.print()

    for idx, (_, row) in enumerate(matches):
        history_display = history_format_rich(row.get("history", ""), latest_only=True)
        line = Text.assemble(
            (f"  [{idx}] ", "white"),
            (row.get("job_position", ""), "bold white"),
            (" @ ", "white"),
            (row.get("company_name", ""), "white"),
            ("  (", "white"),
        )
        line.append_text(history_display)
        line.append(")", style="white")
        console.print(line)

    console.print()

    choice = typer.prompt(
        "Which one do you want to update?",
        type=int,
        default=0,
        show_default=True,
    )

    if choice < 0 or choice >= len(matches):
        console.print("[bold red]Invalid selection.[/bold red]")
        raise typer.Exit(code=1)

    return matches[choice]


def _show_selected_job(chosen_row: dict) -> None:
    console.print()
    console.print(Text("Selected job:", style=f"bold {rgb(UPDATE)}"))
    console.print(
        Text.assemble(
            (chosen_row.get("job_position", ""), "bold white"),
            (" @ ", rgb(UPDATE)),
            (chosen_row.get("company_name", ""), "white"),
            (", ", rgb(UPDATE)),
            (chosen_row.get("location", ""), "white"),
        )
    )


def _handle_status_update(rows: list[dict], row_index: int, chosen_row: dict, csv_path) -> None:
    current_status_display = history_format_rich(chosen_row.get("history", ""), latest_only=True)

    console.print()
    line = Text("Latest update: ", style="white")
    line.append_text(current_status_display)
    console.print(line)
    console.print()

    console.print(Text("Allowed status values:", style=f"bold {rgb(UPDATE)}"))
    console.print(f"[white]{', '.join(ALLOW_STATUS)}[/white]")
    console.print()

    new_status = typer.prompt("New status").strip()

    if new_status not in ALLOW_STATUS:
        console.print(f"[bold red]Invalid status. Choose one of: {', '.join(ALLOW_STATUS)}[/bold red]")
        raise typer.Exit(code=1)

    update_history(rows, row_index, new_status)
    write_rows(csv_path, rows)

    new_status_color = STATUS_COLORS.get(new_status, (240, 240, 240))
    console.print()
    console.print(
        Text.assemble(
            ("Updated ", f"bold {rgb(UPDATE)}"),
            ("status to ", "white"),
            (new_status, f"bold {rgb(new_status_color)}"),
            (" and ", "white"),
            ("saved", rgb(SAVE)),
            (" to ", "white"),
            (str(csv_path), "white"),
        )
    )


def _handle_field_update(rows: list[dict], row_index: int, csv_path) -> None:
    console.print()
    console.print(Text("Editable fields:", style=f"bold {rgb(UPDATE)}"))
    console.print()
    for field_name in EDITABLE_FIELDS:
        console.print(f"  [{rgb(UPDATE)}]•[/{rgb(UPDATE)}] {field_name}")
    console.print()

    field_to_edit = typer.prompt("Entry you want to edit").strip()

    if field_to_edit not in EDITABLE_FIELDS:
        console.print(f"[bold red]Invalid field. Choose one of: {', '.join(EDITABLE_FIELDS)}[/bold red]")
        raise typer.Exit(code=1)

    new_value = typer.prompt(f"New {field_to_edit}").strip()

    edit_entry(rows, row_index, field_to_edit, new_value)
    write_rows(csv_path, rows)

    console.print()
    console.print(
        Text.assemble(
            ("Edited ", f"bold {rgb(UPDATE)}"),
            (field_to_edit, "bold white"),
            (" to ", "white"),
            (new_value, "white"),
            (" and ", "white"),
            ("saved", rgb(SAVE)),
            (" to ", "white"),
            (str(csv_path), "white"),
        )
    )


def _handle_erase(rows: list[dict], row_index: int, chosen_row: dict, csv_path) -> None:
    console.print()
    console.print(Text("Row selected for erase:", style=f"bold {rgb(UPDATE)}"))
    console.print(
        Text.assemble(
            (chosen_row.get("job_position", ""), "bold white"),
            (" @ ", rgb(UPDATE)),
            (chosen_row.get("company_name", ""), "white"),
        )
    )
    console.print()

    confirmed = typer.confirm("Erase this row?", default=False)
    if not confirmed:
        console.print("[white]Erase cancelled.[/white]")
        raise typer.Exit()

    rows.pop(row_index)
    write_rows(csv_path, rows)

    console.print()
    console.print(
        Text.assemble(
            ("Erased ", f"bold {rgb(UPDATE)}"),
            (chosen_row.get("job_position", ""), "bold white"),
            (" @ ", rgb(UPDATE)),
            (chosen_row.get("company_name", ""), "white"),
            ("saved", rgb(SAVE)),
            (" to ", "white"),
            (str(csv_path), "white"),
        )
    )
