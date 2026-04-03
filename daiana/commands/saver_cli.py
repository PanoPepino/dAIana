import typer

from daiana.core.saver import save_job_in_csv
from daiana.utils.constants import COMMAND_COLORS
from daiana.utils.styles import command_banner, rgb_to_ansi


def register_save_command(app: typer.Typer) -> None:
    @app.command("save", help="Save a new job you have applied to in a .csv file.")
    def save_job(
        career: str = typer.Option(..., "--career", "-cp", help='Career path (e.g., "software")'),
    ) -> None:
        """Save jobs you have applied to in a .csv file for easier tracking."""
        command_banner("dAIana saver: Store your job hunt trophies", COMMAND_COLORS["save"])

        typer.echo(typer.style("Fill in the fields below:", fg=rgb_to_ansi(COMMAND_COLORS["save"])))
        typer.echo()

        job_position = typer.prompt(typer.style("1) Job position", fg="white", bold=True))
        company_name = typer.prompt(typer.style("2) Company name", fg="white", bold=True))
        location     = typer.prompt(typer.style("3) Location",     fg="white", bold=True), default="")
        job_link     = typer.prompt(
            typer.style("4) Link to job description ", fg="white", bold=True)
            + typer.style("(press ENTER if none)", fg="white"),
            default="",
        )
        typer.echo()

        csv_path = save_job_in_csv(
            career=career,
            job_position=job_position,
            company_name=company_name,
            location=location,
            job_link=job_link,
        )
        typer.echo(
            typer.style("Saved ", fg=rgb_to_ansi(COMMAND_COLORS["save"]), bold=True)
            + typer.style("Job info stored at: ", fg="white")
            + typer.style(f"{csv_path}_jobs.csv")
        )
        typer.echo()
