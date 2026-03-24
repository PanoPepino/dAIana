import click
from daiana.updater import *
from daiana.allowed import *
from daiana.utils import history_formatter


def register_update_command(cli: click.Group) -> None:
    @cli.command("update", help="Update the status of a saved job application.")
    def update_job() -> None:
        click.echo()
        click.echo(click.style("┌──────────────────────────────────────────────────────────┐", fg="bright_yellow"))
        click.echo(click.style("│      dAIana updater: track your job application status   │", fg="bright_yellow", bold=True))
        click.echo(click.style("└──────────────────────────────────────────────────────────┘", fg="bright_yellow"))
        click.echo()

        click.echo(click.style("Fill in the fields below:", fg="yellow"))
        click.echo()
        career_path = click.prompt(
            click.style("1) Career path", fg='white', bold=True)
        )
        position = click.prompt(
            click.style("2) Job position", fg='white', bold=True)
        )
        company = click.prompt(
            click.style("3) Company name", fg='white', bold=True)
        )

        try:
            rows, csv_path = load_rows_career(career_path)
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
            click.echo(click.style(f"Found {len(matches)} matching jobs:", fg="bright_yellow", bold=True))
            for idx, (_, row) in enumerate(matches):
                line = (
                    click.style(f"  [{idx}] ", fg="white")
                    + click.style(row.get("job_position", ""), fg="white", bold=True)
                    + click.style(" @ ", fg="white")
                    + click.style(row.get("company_name", ""), fg="white")
                    + click.style("  (status=", fg="white")
                    + click.style(row.get("status", ""), fg="cyan")
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
        click.echo(click.style("Selected job:", fg="bright_yellow", bold=True))
        click.echo("")
        click.echo(
            click.style(chosen_row.get("job_position", ""), fg="white", bold=True)
            + click.style(" @ ", fg="white")
            + click.style(chosen_row.get("company_name", ""), fg="white")
        )

        current_status = chosen_row.get("status", "")  # Needs to be fixed
        click.echo(
            click.style("Current status: ", fg="white")
            + click.style(current_status or "-", fg="cyan", bold=True)
        )

        click.echo()
        new_status = click.prompt(
            click.style("New status", fg='white', bold=True),
            type=click.Choice(ALLOW_STATUS),
        )

        new_status_display = STATUS_COLORS.get(new_status, 'white')

        update_rows(rows, row_index, new_status)
        write_rows(csv_path, rows)

        click.echo()
        click.echo(
            click.style("Updated status to ", fg="yellow", bold=True)
            + click.style(f"{new_status}", fg=new_status_display, bold=True)
            + click.style(" and saved to ", fg="cyan")
            + click.style(str(csv_path), fg="white")
        )
        click.echo()
