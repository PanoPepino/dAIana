import click

from daiana.utils.for_csv import history_format_display
from daiana.utils.constants import ALLOW_STATUS, FIELDNAMES, STATUS_COLORS, COMMAND_COLORS
from daiana.utils.styles import DaianaCommand, command_banner
from daiana.core.updater import (
    load_rows_career,
    find_rows,
    update_history,
    edit_entry,
    write_rows,
)


def register_update_command(cli: click.Group) -> None:
    @cli.command("update", cls=DaianaCommand, help="Update the status of a saved job application.")
    @click.option("--career", "-cp", required=True, help='Career path (e.g., "software")')
    @click.option("--status", "-s", is_flag=True, help="Update application status")
    @click.option("--field", "-f", is_flag=True, help="Edit any other field")
    def update_job(career: str, status: bool, field: bool) -> None:
        command_banner(
            "dAIana updater: Update/Edit your job hunt information ",
            COMMAND_COLORS["update"],
        )

        _validate_update_mode(status, field)
        position, company = _prompt_job_identity()

        try:
            rows, csv_path = load_rows_career(career)
        except FileNotFoundError as exc:
            raise click.ClickException(str(exc)) from exc

        matches = find_rows(rows, position, company)
        if not matches:
            raise click.ClickException("No matching job found with those fields.")

        row_index, chosen_row = _pick_matching_row(matches)
        _show_selected_job(chosen_row)

        if status:
            _handle_status_update(rows, row_index, chosen_row, csv_path)
        else:
            _handle_field_update(rows, row_index, csv_path)

        click.echo()


def _validate_update_mode(status: bool, field: bool) -> None:
    if status and field:
        raise click.ClickException("Choose only one mode: --status or --field")
    if not status and not field:
        raise click.ClickException("Choose one mode: --status or --field")


def _prompt_job_identity() -> tuple[str, str]:
    click.echo(click.style("Fill in fields below:", fg=COMMAND_COLORS["update"]))
    click.echo()

    position = click.prompt(click.style("1) Job Position", fg="white", bold=True))
    company = click.prompt(click.style("2) Company Name", fg="white", bold=True))
    return position, company


def _pick_matching_row(matches: list[tuple[int, dict]]) -> tuple[int, dict]:
    if len(matches) == 1:
        return matches[0]

    click.echo()
    click.echo(click.style(f"Found {len(matches)} matching jobs:", fg=COMMAND_COLORS["update"], bold=True))

    for idx, (_, row) in enumerate(matches):
        history_display = history_format_display(row.get("history", ""))
        line = (
            click.style(f"  [{idx}] ", fg="white")
            + click.style(row.get("job_position", ""), fg="white", bold=True)
            + click.style(" @ ", fg="white")
            + click.style(row.get("company_name", ""), fg="white")
            + click.style("  (", fg="white")
            + history_display
            + click.style(")", fg="white")
        )
        click.echo(line)

    click.echo()

    choice = click.prompt(
        click.style("Which one do you want to update?", bold=True),
        type=click.IntRange(0, len(matches) - 1),
        default=0,
        show_default=True,
    )
    return matches[choice]


def _show_selected_job(chosen_row: dict) -> None:
    click.echo()
    click.echo(click.style("Selected job:", fg=COMMAND_COLORS["update"], bold=True))
    click.echo()
    click.echo(
        click.style(chosen_row.get("job_position", ""), fg="white", bold=True)
        + click.style(" @ ", fg=COMMAND_COLORS["update"])
        + click.style(chosen_row.get("company_name", ""), fg="white")
        + click.style(", ", fg=COMMAND_COLORS["update"])
        + click.style(chosen_row.get("city", ""), fg="white")
    )


def _handle_status_update(rows: list[dict], row_index: int, chosen_row: dict, csv_path) -> None:
    current_status_display = history_format_display(chosen_row.get("history", ""))

    click.echo(
        click.style("Latest update: ", fg="white")
        + current_status_display
    )

    click.echo()
    new_status = click.prompt(
        click.style("New status", fg="white", bold=True),
        type=click.Choice(ALLOW_STATUS),
    )

    update_history(rows, row_index, new_status)
    write_rows(csv_path, rows)

    new_status_color = STATUS_COLORS.get(new_status, "white")
    click.echo()
    click.echo(
        click.style("Updated ", fg=COMMAND_COLORS["update"], bold=True)
        + click.style("status to ", fg="white")
        + click.style(new_status, fg=new_status_color, bold=True)
        + click.style(" and ", fg="white")
        + click.style("saved ", fg=COMMAND_COLORS["save"])
        + click.style(f"to {csv_path}", fg="white")
    )


def _handle_field_update(rows: list[dict], row_index: int, csv_path) -> None:
    field_to_edit = click.prompt(
        click.style("Entry you want to edit", fg="white", bold=True),
        type=click.Choice(FIELDNAMES),
    )

    new_value = click.prompt(
        click.style(f"New {field_to_edit}", fg="white", bold=True)
    )

    edit_entry(rows, row_index, field_to_edit, new_value)
    write_rows(csv_path, rows)

    click.echo()
    click.echo(
        click.style("Edited ", fg=COMMAND_COLORS["update"], bold=True)
        + click.style(f"{field_to_edit} to {new_value}", fg="white")
        + click.style(" and saved to ", fg=COMMAND_COLORS["save"])
        + click.style(str(csv_path), fg="white")
    )
