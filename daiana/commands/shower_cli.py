import click
from daiana.core.shower import get_last_jobs
from daiana.utils.constants import STATUS_COLORS
from daiana.utils.for_csv import history_format_display


def register_show_command(cli: click.Group) -> None:
    @cli.command("show")
    @click.option('--career', '-cp', required=True, help='Career path (e.g., "software")')
    @click.option('--rows', '-rj', type=int, default=20, help='Number of recent jobs')
    def show_job(career: str, rows: int) -> None:
        click.echo()
        click.echo(click.style("┌──────────────────────────────────────────────────────────┐", fg="magenta"))
        click.echo(click.style("│           dAIana shower: Inspect your saved jobs         │", fg="magenta", bold=True))
        click.echo(click.style("└──────────────────────────────────────────────────────────┘", fg="magenta"))
        click.echo()
        click.echo(click.style("--- Show off your previous hunting trophies ---", fg="magenta"))
        click.echo()

        try:
            rows_data, csv_path = get_last_jobs(career, rows)
        except FileNotFoundError as exc:
            click.echo(click.style(str(exc), fg="red"))
            return

        if not rows_data:
            click.echo(click.style("No jobs saved yet for this career path.", fg="yellow"))
            return

        click.echo(
            click.style("Showing ", fg="magenta", bold=True)
            + click.style(f"last {len(rows_data)} job(s) ", fg="white")
            + click.style("from ", fg="white")
            + click.style(str(csv_path), fg="white")
        )
        click.echo()

        # Header
        click.echo(click.style("-" * 110, fg='magenta'))
        click.echo(
            click.style("POSITION                 ", fg="white", bold=True)
            + click.style("| ", fg="magenta")
            + click.style("COMPANY       ", fg="white", bold=True)
            + click.style("| ", fg="magenta")
            + click.style("LOCATION    ", fg="white", bold=True)
            + click.style("| ", fg="magenta")
            + click.style("HISTORY", fg="white", bold=True)
        )
        click.echo(click.style("-" * 110, fg='magenta'))

        # Rows
        for row in rows_data:
            pos = (row.get("job_position") or "")[:25]
            company = (row.get("company_name") or "")[:12]
            location = (row.get("city") or "")[:12]
            history_json = row.get('history', "")

            colored_history = history_format_display(history_json, latest_only=False)

            line = (
                click.style(f"{pos:25}", fg="white")
                + click.style("| ", fg="magenta")
                + click.style(f"{company:14}", fg="white")
                + click.style("| ", fg="magenta")
                + click.style(f"{location:12}", fg="white")
                + click.style("| ", fg="magenta")
                + colored_history
            )
            click.echo(line)

        click.echo()
        click.echo()
