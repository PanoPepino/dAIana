"""
contacts_comm.py — CLI sub-commands for the network contacts tracker.

Three sub-commands are exposed:
  daiana contacts save    — prompt and store a new contact
  daiana contacts show    — display the contacts table
  daiana contacts update  — edit a field or erase a contact

Contacts are career-agnostic: a single global file at job_tracking/contacts.csv.
"""
from __future__ import annotations

from datetime import date

import typer
from rich.console import Console
from rich.text import Text

from daiana.infra.csv_repository import load_contacts, write_contacts
from daiana.services.contacts_service import (
    save_contact_entry,
    get_last_contacts,
    find_contacts,
    update_contact_field,
    erase_contact,
)
from daiana.utils.constants import EDITABLE_CONTACT_FIELDS
from daiana.utils.design.colors import COMMAND_COLORS
from daiana.utils.design.styles import contacts_table
from daiana.utils.design.ui import DaianaUI, rgb

# ── App setup ─────────────────────────────────────────────────────────────────

app = typer.Typer(
    help="Manage your professional network contacts.",
    no_args_is_help=True,
    rich_markup_mode="rich",
)

console = Console()
ui = DaianaUI()

# Shortcut to avoid repeating dict lookups
COLOR = COMMAND_COLORS["contacts"]


# ── daiana contacts save ──────────────────────────────────────────────────────

@app.command("save")
def contacts_save() -> None:
    """Prompt for contact details and store them in the global contacts table."""
    console.print()
    ui.rule("dAIana contacts · save", color=COLOR)
    console.print()
    ui.info("[italic]Add a new contact to your network[/italic]", color=COLOR)
    console.print()

    # Prompt for each field; date defaults to today so the user can just hit Enter
    console.print(f"[{rgb(COLOR)}]Fill in the fields below:[/{rgb(COLOR)}]")
    console.print()

    contact_name    = typer.prompt("1) Contact name").strip()
    company         = typer.prompt("2) Company").strip()
    location        = typer.prompt("3) Location", default="", show_default=False).strip()
    email           = typer.prompt("4) Email",    default="", show_default=False).strip()
    # Default date is today in ISO format (YYYY-MM-DD) — user can override
    today           = date.today().isoformat()
    date_of_contact = typer.prompt(
        f"5) Date of contact (ENTER = {today})",
        default=today,
        show_default=False,
    ).strip()

    console.print()

    csv_path = save_contact_entry(
        contact_name=contact_name,
        company=company,
        location=location,
        email=email,
        date_of_contact=date_of_contact,
    )

    console.print(
        Text.assemble(
            ("Saved  ", f"bold {rgb(COLOR)}"),
            ("Contact stored at: ", "white"),
            (str(csv_path), "white"),
        )
    )
    console.print()


# ── daiana contacts show ──────────────────────────────────────────────────────

@app.command("show")
def contacts_show(
    rows: int = typer.Option(20, "--rows", "-r", min=1, help="Number of recent contacts to display."),
) -> None:
    """Display the contacts table (most recent N entries)."""
    console.print()
    ui.rule("dAIana contacts · show", color=COLOR)
    console.print()
    ui.info("[italic]Your professional network[/italic]", color=COLOR)
    console.print()

    try:
        rows_data, csv_path, total = get_last_contacts(rows)
    except FileNotFoundError as exc:
        console.print(f"[bold red]{exc}[/bold red]")
        raise typer.Exit(code=1)

    if not rows_data:
        console.print(f"[bold {rgb(COLOR)}]No contacts saved yet.[/bold {rgb(COLOR)}]")
        console.print(f"  Run [bold]daiana contacts save[/bold] to add your first contact.")
        raise typer.Exit()

    # Render the Rich table
    console.print(contacts_table(rows_data))
    console.print()

    # Summary line at the bottom
    console.print(
        Text.assemble(
            ("Showing ", rgb(COLOR)),
            (f"{len(rows_data)} contact(s) ", f"bold {rgb(COLOR)}"),
            ("from ", "white"),
            (str(csv_path), "white"),
        )
    )
    console.print(
        Text.assemble(
            ("Total contacts: ", rgb(COLOR)),
            (str(total), "bold white"),
        )
    )
    console.print()


# ── daiana contacts update ────────────────────────────────────────────────────

@app.command("update")
def contacts_update(
    field: bool = typer.Option(False, "--field", "-f", help="Edit a field on an existing contact."),
    erase: bool = typer.Option(False, "--erase", "-e", help="Erase a contact row."),
) -> None:
    """
    Update or erase an existing contact.

    Use --field to edit any column value, or --erase to remove the row.
    The contact is identified by name + company (prompted interactively).
    """
    console.print()
    ui.rule("dAIana contacts · update", color=COLOR)
    console.print()
    ui.info("[italic]Update or erase a contact[/italic]", color=COLOR)
    console.print()

    # Validate that exactly one mode flag was passed
    if not field and not erase:
        console.print(f"[bold red]Choose a mode: --field or --erase[/bold red]")
        raise typer.Exit(code=1)
    if field and erase:
        console.print(f"[bold red]Choose only one mode: --field or --erase[/bold red]")
        raise typer.Exit(code=1)

    # Load the contacts CSV
    try:
        rows, csv_path = load_contacts()
    except FileNotFoundError as exc:
        console.print(f"[bold red]{exc}[/bold red]")
        raise typer.Exit(code=1)

    # Identify the contact to modify
    console.print(f"[{rgb(COLOR)}]Identify the contact:[/{rgb(COLOR)}]")
    console.print()
    contact_name = typer.prompt("1) Contact name").strip()
    company      = typer.prompt("2) Company").strip()

    matches = find_contacts(rows, contact_name, company)

    if not matches:
        console.print(f"[bold red]No contact found matching '{contact_name}' at '{company}'.[/bold red]")
        raise typer.Exit(code=1)

    # If multiple rows match, let the user pick one
    row_index, chosen_row = _pick_matching_contact(matches)

    # Show what was selected
    console.print()
    console.print(Text("Selected contact:", style=f"bold {rgb(COLOR)}"))
    console.print(
        Text.assemble(
            (chosen_row.get("contact_name", ""), "bold white"),
            (" @ ", rgb(COLOR)),
            (chosen_row.get("company", ""),       "white"),
            (", ",                                 rgb(COLOR)),
            (chosen_row.get("location", ""),       "white"),
        )
    )
    console.print()

    if field:
        _handle_contact_field_update(rows, row_index, csv_path)
    elif erase:
        _handle_contact_erase(rows, row_index, chosen_row, csv_path)

    console.print()


# ── Internal helpers ──────────────────────────────────────────────────────────

def _pick_matching_contact(matches: list[tuple[int, dict]]) -> tuple[int, dict]:
    """Return the single match directly, or prompt the user to choose among duplicates."""
    if len(matches) == 1:
        return matches[0]

    console.print()
    console.print(Text(f"Found {len(matches)} matching contacts:", style=f"bold {rgb(COLOR)}"))
    console.print()

    for idx, (_, row) in enumerate(matches):
        console.print(
            Text.assemble(
                (f"  [{idx}] ", "white"),
                (row.get("contact_name", ""), f"bold {rgb(COLOR)}"),
                (" @ ",                       "white"),
                (row.get("company", ""),       "white"),
                (" — ",                        "dim white"),
                (row.get("date_of_contact", ""), "dim white"),
            )
        )

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


def _handle_contact_field_update(
    rows: list[dict], row_index: int, csv_path
) -> None:
    """Prompt the user to choose a field and a new value, then persist."""
    console.print(Text("Editable fields:", style=f"bold {rgb(COLOR)}"))
    console.print()
    for f in EDITABLE_CONTACT_FIELDS:
        console.print(f"  [{rgb(COLOR)}]·[/{rgb(COLOR)}] {f}")
    console.print()

    field_to_edit = typer.prompt(
        "Field to edit",
        type=typer.Choice(EDITABLE_CONTACT_FIELDS),
    )
    new_value = typer.prompt(f"New value for '{field_to_edit}'").strip()

    # Apply the in-memory change and write to disk
    update_contact_field(rows, row_index, field_to_edit, new_value)
    write_contacts(rows)

    console.print()
    console.print(
        Text.assemble(
            ("Edited  ", f"bold {rgb(COLOR)}"),
            (field_to_edit, "bold white"),
            (" → ",         rgb(COLOR)),
            (new_value,     "white"),
            (" — saved to ", "white"),
            (str(csv_path), "white"),
        )
    )


def _handle_contact_erase(
    rows: list[dict], row_index: int, chosen_row: dict, csv_path
) -> None:
    """Confirm with the user, then remove the row and persist."""
    console.print(
        Text("⚠ You are about to erase this contact:", style=f"bold {rgb(COMMAND_COLORS['hunt'])}")
    )
    console.print(
        Text.assemble(
            (chosen_row.get("contact_name", ""), "bold white"),
            (" @ ",                               rgb(COLOR)),
            (chosen_row.get("company", ""),        "white"),
        )
    )
    console.print()

    confirmed = typer.confirm("Are you sure you want to erase this contact?", default=False)
    if not confirmed:
        console.print(Text("Erase cancelled.", style="dim white"))
        raise typer.Exit()

    # Remove the row in memory, then flush to disk
    erase_contact(rows, row_index)
    write_contacts(rows)

    console.print()
    console.print(
        Text.assemble(
            ("Erased  ", f"bold {rgb(COMMAND_COLORS['hunt'])}"),
            (chosen_row.get("contact_name", ""), "bold white"),
            (" @ ",                               rgb(COLOR)),
            (chosen_row.get("company", ""),        "white"),
            (" — saved to ",                       "white"),
            (str(csv_path),                        "white"),
        )
    )
