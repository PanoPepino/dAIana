import typer

from daiana.utils.for_csv import history_format_display
from daiana.utils.constants import ALLOW_STATUS, FIELDNAMES, STATUS_COLORS, COMMAND_COLORS
from daiana.utils.styles import command_banner, rgb_to_ansi
from daiana.core.updater import (
    load_rows_career,
    find_rows,
    update_history,
    edit_entry,
    write_rows,
)


def register_update_command(app: typer.Typer) -> None:
    @app.command("update", help="Update the status of a saved job application.")
    def update_job(
        career: str  = typer.Option(..., "--career", "-cp", help='Career path (e.g., "software")'),
        status: bool = typer.Option(False, "--status", "-s", help="Update application status"),
        field:  bool = typer.Option(False, "--field",  "-f", help="Edit any other field"),
    ) -> None:
        command_banner("dAIana updater: Update/Edit your job hunt information", COMMAND_COLORS["update"])

        _validate_update_mode(status, field)
        position, company = _prompt_job_identity()

        try:
            rows, csv_path = load_rows_career(career)
        except FileNotFoundError as exc:
            typer.secho(str(exc), fg="red")
            raise typer.Exit(1)

        matches = find_rows(rows, position, company)
        if not matches:
            typer.secho("No matching job found with those fields.", fg="red")
            raise typer.Exit(1)

        row_index, chosen_row = _pick_matching_row(matches)
        _show_selected_job(chosen_row)

        if status:
            _handle_status_update(rows, row_index, chosen_row, csv_path)
        else:
            _handle_field_update(rows, row_index, csv_path)

        typer.echo()


def _validate_update_mode(status: bool, field: bool) -> None:
    if status and field:
        typer.secho("Choose only one mode: --status or --field", fg="red")
        raise typer.Exit(1)
    if not status and not field:
        typer.secho("Choose one mode: --status or --field", fg="red")
        raise typer.Exit(1)


def _prompt_job_identity() -> tuple[str, str]:
    typer.echo(typer.style("Fill in fields below:", fg=rgb_to_ansi(COMMAND_COLORS["update"])))
    typer.echo()
    position = typer.prompt(typer.style("1) Job Position", fg="white", bold=True))
    company  = typer.prompt(typer.style("2) Company Name", fg="white", bold=True))
    return position, company


def _pick_matching_row(matches: list[tuple[int, dict]]) -> tuple[int, dict]:
    if len(matches) == 1:
        return matches[0]

    typer.echo()
    typer.echo(typer.style(f"Found {len(matches)} matching jobs:", fg=rgb_to_ansi(COMMAND_COLORS["update"]), bold=True))

    for idx, (_, row) in enumerate(matches):
        history_display = history_format_display(row.get("history", ""))
        typer.echo(
            typer.style(f"  [{idx}] ", fg="white")
            + typer.style(row.get("job_position", ""), fg="white", bold=True)
            + typer.style(" @ ", fg="white")
            + typer.style(row.get("company_name", ""), fg="white")
            + typer.style("  (", fg="white")
            + history_display
            + typer.style(")", fg="white")
        )
    typer.echo()

    choice = typer.prompt(
        typer.style("Which one do you want to update?", bold=True),
        default=0,
    )
    return matches[int(choice)]


def _show_selected_job(chosen_row: dict) -> None:
    typer.echo()
    typer.echo(typer.style("Selected job:", fg=rgb_to_ansi(COMMAND_COLORS["update"]), bold=True))
    typer.echo()
    typer.echo(
        typer.style(chosen_row.get("job_position", ""), fg="white", bold=True)
        + typer.style(" @ ", fg=rgb_to_ansi(COMMAND_COLORS["update"]))
        + typer.style(chosen_row.get("company_name", ""), fg="white")
        + typer.style(", ", fg=rgb_to_ansi(COMMAND_COLORS["update"]))
        + typer.style(chosen_row.get("city", ""), fg="white")
    )


def _handle_status_update(rows: list[dict], row_index: int, chosen_row: dict, csv_path) -> None:
    current_status_display = history_format_display(chosen_row.get("history", ""))
    typer.echo(typer.style("Latest update: ", fg="white") + current_status_display)
    typer.echo()

    new_status = typer.prompt(
        typer.style("New status", fg="white", bold=True),
        type=typer.Choice(ALLOW_STATUS),
    )
    update_history(rows, row_index, new_status)
    write_rows(csv_path, rows)

    new_status_color = STATUS_COLORS.get(new_status, "white")
    typer.echo()
    typer.echo(
        typer.style("Updated ", fg=rgb_to_ansi(COMMAND_COLORS["update"]), bold=True)
        + typer.style("status to ", fg="white")
        + typer.style(new_status, fg=new_status_color, bold=True)
        + typer.style(" and ", fg="white")
        + typer.style("saved ", fg=rgb_to_ansi(COMMAND_COLORS["save"]))
        + typer.style(f"to {csv_path}", fg="white")
    )


def _handle_field_update(rows: list[dict], row_index: int, csv_path) -> None:
    field_to_edit = typer.prompt(
        typer.style("Entry you want to edit", fg="white", bold=True),
        type=typer.Choice(FIELDNAMES),
    )
    new_value = typer.prompt(typer.style(f"New {field_to_edit}", fg="white", bold=True))

    edit_entry(rows, row_index, field_to_edit, new_value)
    write_rows(csv_path, rows)

    typer.echo()
    typer.echo(
        typer.style("Edited ", fg=rgb_to_ansi(COMMAND_COLORS["update"]), bold=True)
        + typer.style(f"{field_to_edit} to {new_value}", fg="white")
        + typer.style(" and saved to ", fg=rgb_to_ansi(COMMAND_COLORS["save"]))
        + typer.style(str(csv_path), fg="white")
    )
