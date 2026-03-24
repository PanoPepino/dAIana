import click
from daiana.shower import get_last_jobs
from daiana.allowed import STATUS_COLORS
from daiana.utils import *


def register_show_command(cli: click.Group) -> None:

    @cli.command("show")
    def show_job() -> None:
        click.echo()
        click.echo(click.style("┌──────────────────────────────────────────────────────────┐", fg="bright_magenta"))
        click.echo(click.style("│           dAIana shower: inspect your saved jobs         │", fg="bright_magenta", bold=True))
        click.echo(click.style("└──────────────────────────────────────────────────────────┘", fg="bright_magenta"))
        click.echo()

        click.echo(click.style("Fill in the fields below:", fg="magenta"))
        click.echo()
        career_path = click.prompt(
            click.style("1) Career path", fg='white', bold=True))

        n = click.prompt(
            click.style("2) # of recent jobs to inspect", fg='white', bold=True),
            default=5,
            type=int,
            show_default=True,
        )

        try:
            rows, csv_path = get_last_jobs(career_path, n)
        except FileNotFoundError as exc:
            click.echo(click.style(str(exc), fg="red"))
            return

        if not rows:
            click.echo(click.style("No jobs saved yet for this career path.", fg="yellow"))
            return

        click.echo()
        click.echo(
            click.style("Showing ", fg="magenta", bold=True)
            + click.style(f"last {len(rows)} job(s) ", fg="white")
            + click.style("from ", fg="white")
            + click.style(str(csv_path), fg="white")
        )
        click.echo()

        # Header line (DATE ~11, POSITION 25, COMPANY 12, LOCATION 12)
        click.echo(
            click.style("POSITION                 ", fg="white", bold=True)  # 1 + 25
            + click.style("| ", fg="magenta")
            + click.style("COMPANY       ", fg="white", bold=True)    # 1 + 12
            + click.style("| ", fg="magenta")
            + click.style("LOCATION    ", fg="white", bold=True)            # 1 + 12
            + click.style("| ", fg="magenta")
            + click.style("HISTORY", fg="white", bold=True)
        )
        click.echo(click.style("-" * 110, fg='magenta'))

        # Rows
        for row in rows:
            pos = (row.get("job_position") or "")[:25]
            company = (row.get("company_name") or "")[:12]
            location = (row.get("city") or "")[:12]
            history = (row.get('history') or "")
            colored_history = history_formatter(history)

            line = (
                click.style(f"{pos:25}", fg="white")        # POSITION
                + click.style("| ", fg="magenta")
                + click.style(f"{company:14}", fg="white")    # COMPANY
                + click.style("| ", fg="magenta")
                + click.style(f"{location:12}", fg="white")   # LOCATION
                + click.style("| ", fg="magenta")
                + colored_history         # LINK
            )
            click.echo(line)

        click.echo()
        click.echo()
