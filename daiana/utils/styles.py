
from typing import Dict
import click
import json

from rich.text import Text
from rich import box
from rich.table import Table

from daiana.utils.for_csv import get_current_status
from daiana.utils.constants import ALLOW_STATUS
from daiana.utils.ui import STATUS_COLORS, COMMAND_COLORS


def get_status_color(action: str) -> Dict[str, any]:
    """
    Simple function to map a color to its associated status and/or date.
    """
    coloring = STATUS_COLORS.get(action.lower(), "white")
    return {"fg": coloring}


def get_command_color(command: str, color: str) -> str:
    """
    Simple function to map a color to its associated command.
    """
    return click.style(command, fg=color)


def rgb(color: tuple[int, int, int]) -> str:
    """
    To transform color dictionaries in rgb inputs
    """
    r, g, b = color
    return f"rgb({r},{g},{b})"


# Styles to show tables in show, update, etc.
def history_format_rich(history_json: str, latest_only: bool = True) -> Text:
    """Rich Text version of history_format_display for Typer/Rich tables."""
    from rich.text import Text

    action, latest_update = get_current_status(history_json)

    if not action:
        t = Text()
        t.append("-", style="bold red")
        return t

    color_style = get_status_color(action)
    fg = color_style.get("fg", "white")
    bold = color_style.get("bold", False)

    def to_rich_style(fg_val, is_bold: bool) -> str:
        if isinstance(fg_val, tuple):
            r, g, b = fg_val
            base = f"rgb({r},{g},{b})"
        else:
            base = str(fg_val)
        return f"bold {base}" if is_bold else base

    if latest_only:
        t = Text()
        t.append(latest_update, style=to_rich_style(fg, bold))
        return t

    try:
        history = json.loads(history_json)
        t = Text()
        entries = list(sorted(history.keys()))
        for idx, key in enumerate(entries):
            update_day = history[key]
            s = get_status_color(key)
            s_fg = s.get("fg", "white")
            s_bold = s.get("bold", False)
            t.append(update_day, style=to_rich_style(s_fg, s_bold))
            if idx < len(entries) - 1:
                t.append(" · ")
        return t
    except Exception:
        t = Text()
        t.append(str(history_json))
        return t


def status_legend() -> Text:
    legend = Text("Recall that the color legend indicates:  ", style=f"bold {rgb(COMMAND_COLORS['show'])}")
    for idx, state in enumerate(ALLOW_STATUS):
        fg_info = get_status_color(state)
        fg = fg_info.get("fg", "white")
        bold = fg_info.get("bold", False)
        style = f"bold {rgb(fg)}" if bold and isinstance(fg, tuple) else (rgb(fg) if isinstance(fg, tuple) else str(fg))
        legend.append(state, style=style)
        if idx < len(ALLOW_STATUS) - 1:
            legend.append(", ", style="white")
    return legend


def render_history(history_json: str) -> Text:
    return history_format_rich(history_json, latest_only=False)


def jobs_table(rows_data: list[dict]) -> Table:
    table = Table(
        box=box.ROUNDED,
        border_style=rgb(COMMAND_COLORS['show']),
        header_style=f"bold {rgb(COMMAND_COLORS['show'])}",
        show_lines=False,
        expand=True,
        pad_edge=False,
        padding=(0, 1),
    )
    table.add_column("Position", justify="left", no_wrap=False, min_width=10, max_width=20)
    table.add_column("Company", justify="left", no_wrap=False, min_width=12, max_width=16)
    table.add_column("Location", justify="left", no_wrap=False, min_width=8, max_width=8)
    table.add_column("History", justify="left", no_wrap=False, min_width=24)

    for row in rows_data:
        pos = (row.get("job_position") or "").strip()[:30]
        company = (row.get("company_name") or "").strip()[:20]
        location = (row.get("location") or "").strip()[:20]
        history_json = row.get("history") or ""

        table.add_row(
            Text(pos, style="white"),
            Text(company, style="white"),
            Text(location, style="white"),
            render_history(history_json),
        )

    return table


# ── Validation ────────────────────────────────────────────────────────────────

def _validate_mode(status: bool, field: bool, erase: bool) -> None:
    modes = [status, field, erase]
    if sum(modes) > 1:
        console.print(f"[{rgb(UPDATE)}]✘[/{rgb(UPDATE)}] Choose only one mode: --status, --field, or --erase.")
        raise typer.Exit(code=1)
    if sum(modes) == 0:
        console.print(f"[{rgb(UPDATE)}]✘[/{rgb(UPDATE)}] Choose one mode: --status, --field, or --erase.")
        raise typer.Exit(code=1)


# ── Row identification ────────────────────────────────────────────────────────

def _prompt_job_identity() -> tuple[str, str]:
    console.print(f"[{rgb(UPDATE)}]Fill in fields to identify the job:[/{rgb(UPDATE)}]")
    console.print()
    position = typer.prompt("1) Job position")
    company = typer.prompt("2) Company name")
    return position, company


def _pick_matching_row(matches: list[tuple[int, dict]]) -> tuple[int, dict]:
    if len(matches) == 1:
        return matches[0]

    console.print()
    console.print(Text(f"Found {len(matches)} matching jobs:", style=f"bold {rgb(UPDATE)}"))
    console.print()

    for idx, (_, row) in enumerate(matches):
        history_text = history_format_rich(row.get("history", ""), latest_only=True)
        line = Text.assemble(
            (f"  [{idx}] ", "white"),
            (row.get("job_position", ""), f"bold {rgb(UPDATE)}"),
            (" @ ", "white"),
            (row.get("company_name", ""), "white"),
            ("  (", "dim white"),
        )
        line.append_text(history_text)
        line.append(")", style="dim white")
        console.print(line)

    console.print()
    choice = typer.prompt(
        "Which one do you want to update?",
        type=int,
        default=0,
        show_default=True,
    )
    if choice < 0 or choice >= len(matches):
        console.print(f"[{rgb(UPDATE)}]✘[/{rgb(UPDATE)}] Invalid selection.")
        raise typer.Exit(code=1)
    return matches[choice]


def _show_selected_job(chosen_row: dict) -> None:
    console.print()
    console.print(Text("Selected job:", style=f"bold {rgb(UPDATE)}"))
    console.print()
    console.print(
        Text.assemble(
            (chosen_row.get("job_position", ""), f"bold white"),
            (" @ ", rgb(UPDATE)),
            (chosen_row.get("company_name", ""), "white"),
            (", ", rgb(UPDATE)),
            (chosen_row.get("location", ""), "white"),
        )
    )


# ── Mode handlers ─────────────────────────────────────────────────────────────

def _handle_status_update(
    rows: list[dict], row_index: int, chosen_row: dict, csv_path
) -> None:
    current = history_format_rich(chosen_row.get("history", ""), latest_only=True)
    console.print()
    line = Text("Latest status: ", style="white")
    line.append_text(current)
    console.print(line)
    console.print()

    new_status = typer.prompt(
        "New status",
        type=typer.Choice(ALLOW_STATUS),
    )

    update_history(rows, row_index, new_status)
    write_rows(csv_path, rows)

    status_color = STATUS_COLORS.get(new_status, (240, 240, 240))
    console.print()
    console.print(
        Text.assemble(
            ("Updated ", f"bold {rgb(UPDATE)}"),
            ("status to ", "white"),
            (new_status, f"bold {rgb(status_color)}"),
            (" — saved ", "white"),
            (str(csv_path), f"{rgb(SAVE)}"),
        )
    )


def _handle_field_update(
    rows: list[dict], row_index: int, csv_path
) -> None:
    console.print()
    console.print(Text("Editable fields:", style=f"bold {rgb(UPDATE)}"))
    for f in EDITABLE_FIELDS:
        console.print(f"  [{rgb(UPDATE)}]·[/{rgb(UPDATE)}] {f}")
    console.print()

    field_to_edit = typer.prompt(
        "Field to edit",
        type=typer.Choice(EDITABLE_FIELDS),
    )
    new_value = typer.prompt(f"New value for {field_to_edit}")

    edit_entry(rows, row_index, field_to_edit, new_value)
    write_rows(csv_path, rows)

    console.print()
    console.print(
        Text.assemble(
            ("Edited ", f"bold {rgb(UPDATE)}"),
            (f"{field_to_edit}", "bold white"),
            (" → ", rgb(UPDATE)),
            (new_value, "white"),
            (" — saved ", "white"),
            (str(csv_path), rgb(SAVE)),
        )
    )


def _handle_erase(
    rows: list[dict], row_index: int, chosen_row: dict, csv_path
) -> None:
    console.print()
    console.print(Text("⚠ You are about to erase this entry:", style=f"bold {rgb(COMMAND_COLORS['hunt'])}"))
    console.print()
    console.print(
        Text.assemble(
            (chosen_row.get("job_position", ""), "bold white"),
            (" @ ", rgb(UPDATE)),
            (chosen_row.get("company_name", ""), "white"),
        )
    )
    console.print()

    confirm = typer.confirm("Are you sure you want to erase this row?", default=False)
    if not confirm:
        console.print(Text("Erase cancelled.", style="dim white"))
        raise typer.Exit()

    rows.pop(row_index)
    write_rows(csv_path, rows)

    console.print()
    console.print(
        Text.assemble(
            ("Erased ", f"bold {rgb(COMMAND_COLORS['hunt'])}"),
            (chosen_row.get("job_position", ""), "bold white"),
            (" @ ", rgb(UPDATE)),
            (chosen_row.get("company_name", ""), "white"),
            (" — saved ", "white"),
            (str(csv_path), rgb(SAVE)),
        )
    )
