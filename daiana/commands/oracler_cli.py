import typer
from pathlib import Path

from daiana.utils.for_oracle import edit_oracle_dict
from daiana.core.oracler import run_oracle_pipeline
from daiana.utils.styles import command_banner, rgb_to_ansi
from daiana.utils.constants import COMMAND_COLORS


def register_oracle_command(app: typer.Typer) -> None:
    @app.command("oracle", help="Ask AI to tune CV & letter for a position.")
    def consult_oracle(
        url:       str  = typer.Option(..., "-u", "--url",    help="Job URL to scrape and parse as JSON oracle record."),
        csv_path:  Path = typer.Option(Path("job_tracking"), "--csv-path", show_default=True, help="CSV file path reserved for existing daiana logic."),
        extract:   bool = typer.Option(False, "--extract",   help="Extract basic information from the job position."),
        tailor_cl: bool = typer.Option(False, "--tailor_cl", help="Generate simple tailored cover-letter sentences from the job description."),
    ) -> None:
        command_banner("dAIana oracle: Ask guidance to the Oracle", COMMAND_COLORS["oracle"])

        if not extract and not tailor_cl:
            typer.secho("Use at least one flag: --extract and/or --tailor_cl", fg="red")
            raise typer.Exit(1)

        try:
            if extract and tailor_cl:
                typer.secho("Extracting job information and crafting tailored sentence(s) ...", fg=rgb_to_ansi(COMMAND_COLORS["oracle"]))
            elif extract:
                typer.secho("Extracting information of your next trophy ...", fg=rgb_to_ansi(COMMAND_COLORS["oracle"]))
            else:
                typer.secho("Tailoring your requested sentence(s) ...", fg=rgb_to_ansi(COMMAND_COLORS["oracle"]))

            typer.echo()

            result = run_oracle_pipeline(url=url, extract=extract, tailor_cl=tailor_cl)

        except ValueError as exc:
            typer.secho(str(exc), fg="red")
            raise typer.Exit(1)
        except Exception as exc:
            typer.secho(f"Oracle failed: {exc}", fg="red")
            raise typer.Exit(1)

        if not isinstance(result, dict) or not result:
            typer.secho("Oracle returned an empty or invalid result.", fg="red")
            raise typer.Exit(1)

        typer.secho("Oracle result:", fg=rgb_to_ansi(COMMAND_COLORS["oracle"]))
        typer.echo()

        for key, value in result.items():
            typer.echo(f"{key:17}: {value}")

        typer.echo()

        if typer.confirm(
            typer.style("Would you like to modify this information?", fg=rgb_to_ansi(COMMAND_COLORS["oracle"])),
            default=False,
        ):
            result = edit_oracle_dict(result)
            typer.echo()
            typer.secho("The new fields are:", fg=rgb_to_ansi(COMMAND_COLORS["oracle"]))
            for key, value in result.items():
                typer.echo(f"{key:17}: {value}")
            typer.echo()
