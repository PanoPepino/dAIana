import click
from daiana.utils.for_csv import history_format_display
from daiana.utils.constants import ALLOW_STATUS, FIELDNAMES, STATUS_COLORS
from daiana.utils.styles import *
from daiana.core.updater import edit_entry, load_rows_career, find_rows, update_history, write_rows


def register_update_command(cli: click.Group) -> None:
    @cli.command("update", help="Update the status of a saved job application.")
    @click.option('--career', '-cp', required=True, help='Career path (e.g., "software")')
    @click.option('--status', '-s', is_flag=True, help='To update status of your application')
    @click.option('--field', '-i', is_flag=True, help='To edit any other field of your application')
    def update_job(career: str, status: bool, field: bool) -> None:

        # Banner
        command_banner(
            "dAIana updater: Update/Edit your job hunt information ",
            COMMAND_COLORS['update']
        )

        click.echo(click.style("Fill in fields below:", fg=COMMAND_COLORS['update']))
        click.echo()

        # Inputs
        position = click.prompt(click.style("1) Job Position", fg='white', bold=True))
        company = click.prompt(click.style("2) Company Name", fg='white', bold=True))

        try:
            rows, csv_path = load_rows_career(career)
        except FileNotFoundError as exc:
            click.echo(click.style(str(exc), fg="red"))
            return

        matches = find_rows(rows, position, company)

        if not matches:
            click.echo(click.style("No matching job found with those fields.", fg="red"))
            return

        # Let user pick if multiple matches
        if len(matches) > 1:
            click.echo()
            click.echo(click.style(f"Found {len(matches)} matching jobs:", fg=COMMAND_COLORS['update'], bold=True))
            for idx, (_, row) in enumerate(matches):
                history_display = history_format_display(row.get("history", ""))
                line = (
                    click.style(f"  [{idx}] ", fg="white")
                    + click.style(row.get("job_position", ""), fg="white", bold=True)
                    + click.style(" @ ", fg="white")
                    + click.style(row.get("company_name", ""), fg="white")
                    + click.style("  (", fg="white")
                    + history_display  # Colored latest status!
                    + click.style(")", fg="white")
                )
                click.echo(line)
            click.echo()
            choice = click.prompt(
                click.style("Which one do you want to update?", bold=True),
                type=int,
                default=0,
                show_default=True,
            )
            row_index, chosen_row = matches[choice]
        else:
            row_index, chosen_row = matches[0]

        click.echo()
        click.echo(click.style("Selected job:", fg=COMMAND_COLORS['update'], bold=True))
        click.echo("")
        click.echo(
            click.style(chosen_row.get("job_position", ""), fg="white", bold=True)
            + click.style(" @ ", fg=COMMAND_COLORS['update'])
            + click.style(chosen_row.get("company_name", ""), fg="white")
            + click.style(", ", fg=COMMAND_COLORS['update'])
            + click.style(chosen_row.get("city", ""), fg='white')
        )

        if status:
            current_status_display = history_format_display(chosen_row.get("history", ""))
            click.echo(
                click.style("Latest update: ", fg="white")
                + current_status_display
            )

            click.echo()
            new_status = click.prompt(
                click.style("New status", fg='white', bold=True),
                type=click.Choice(ALLOW_STATUS))

            # Update and save
            update_history(rows, row_index, new_status)
            write_rows(csv_path, rows)

            # Confirmation
            new_status_display = STATUS_COLORS.get(new_status, 'white')
            click.echo()
            click.echo(
                click.style("Updated ", fg="yellow", bold=True)
                + click.style(" status to ", fg='white')
                + click.style(new_status, fg=new_status_display, bold=True)
                + click.style(" and ", fg='white')
                + click.style("saved ", fg="cyan")
                + click.style(f"to {str(csv_path)}", fg="white"))

        elif field:
            field_to_edit = click.prompt(click.style("Entry you want to edit", fg='white',
                                                     bold=True), type=click.Choice(FIELDNAMES))

            new_field = click.prompt(click.style(f"New {field_to_edit}",
                                     fg='white', bold=True))

            # Update and save
            edit_entry(rows, row_index, field_to_edit, new_field)
            write_rows(csv_path, rows)

            # Confirmation
            click.echo()
            click.echo(
                click.style(f"Edited ", fg="yellow", bold=True)
                + click.style(f"{field_to_edit} to {new_field}", fg='white')
                + click.style(" and saved to ", fg="cyan")
                + click.style(str(csv_path), fg="white"))

        click.echo()
