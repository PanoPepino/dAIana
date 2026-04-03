import typer

from daiana.core.shower import get_last_jobs
from daiana.utils.constants import COMMAND_COLORS, ALLOW_STATUS
from daiana.utils.for_csv import history_format_display, get_status_color
from daiana.utils.styles import command_banner, rgb_to_ansi


def register_show_command(app: typer.Typer) -> None:
    @app.command("show", help="Track previous applied jobs and their status.")
    def show_job(
        career: str = typer.Option(..., "--career", "-cp", help='Career path (e.g., "software")'),
        rows:   int = typer.Option(20,  "--rows",   "-rj", help="Number of recent jobs"),
    ) -> None:
        """Show your tracked job applications of a given career path."""
        command_banner("dAIana shower: Inspect previous hunting trophies", COMMAND_COLORS["show"])

        try:
            rows_data, csv_path = get_last_jobs(career, rows)
        except FileNotFoundError as exc:
            typer.secho(str(exc), fg="red")
            return

        if not rows_data:
            typer.secho("No jobs saved yet for this career path.", fg="yellow")
            return

        typer.echo(
            typer.style("Showing ",           fg=rgb_to_ansi(COMMAND_COLORS["show"]), bold=True)
            + typer.style(f"last {len(rows_data)} job(s) ", fg="white")
            + typer.style("from ", fg="white")
            + typer.style(str(csv_path), fg="white")
        )
        typer.echo()

        states_line = ", ".join(
            typer.style(state, **get_status_color(state)) for state in ALLOW_STATUS
        )
        typer.echo(
            typer.style("Recall that the color legend indicates:  ", fg=rgb_to_ansi(COMMAND_COLORS["show"]))
            + states_line
        )
        typer.echo()

        sep = typer.style("-" * 110, fg=rgb_to_ansi(COMMAND_COLORS["show"]))
        typer.echo(sep)
        typer.echo(
            typer.style("POSITION             ", fg="white", bold=True)
            + typer.style("| ", fg=rgb_to_ansi(COMMAND_COLORS["show"]))
            + typer.style("COMPANY        ",     fg="white", bold=True)
            + typer.style("| ", fg=rgb_to_ansi(COMMAND_COLORS["show"]))
            + typer.style("LOCATION      ",      fg="white", bold=True)
            + typer.style("| ", fg=rgb_to_ansi(COMMAND_COLORS["show"]))
            + typer.style("HISTORY",             fg="white", bold=True)
        )
        typer.echo(sep)

        for row in rows_data:
            pos      = (row.get("job_position") or "")[:20]
            company  = (row.get("company_name")  or "")[:12]
            location = (row.get("location")      or "")[:14]
            colored_history = history_format_display(row.get("history", ""), latest_only=False)

            typer.echo(
                typer.style(f"{pos:21}",      fg="white")
                + typer.style("| ", fg=rgb_to_ansi(COMMAND_COLORS["show"]))
                + typer.style(f"{company:15}",  fg="white")
                + typer.style("| ", fg=rgb_to_ansi(COMMAND_COLORS["show"]))
                + typer.style(f"{location:14}", fg="white")
                + typer.style("| ", fg=rgb_to_ansi(COMMAND_COLORS["show"]))
                + colored_history
            )

        typer.echo()
