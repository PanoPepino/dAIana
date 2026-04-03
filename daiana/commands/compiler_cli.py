import typer
from typing import Optional

from daiana.core.compiler import _resolve_mode, compile_with_data
from daiana.core.saver import save_job_in_csv
from daiana.utils.styles import command_banner, rgb_to_ansi
from daiana.utils.constants import COMMAND_COLORS


def register_compile_command(app: typer.Typer) -> None:
    @app.command("compile", help="Compile CV or cover letter for a job position. Optional saving in .csv database.")
    def compile_from_template(
        cv:       bool = typer.Option(False, "--cv",       help="CV mode"),
        cl:       bool = typer.Option(False, "--cl",       help="Cover letter mode"),
        username: str  = typer.Option("user_name", "--username", "-un", help="Your name for PDF filename"),
        verbose:  bool = typer.Option(False, "--verbose",  help="Show LaTeX compilation output"),
    ) -> None:
        command_banner(
            "dAIana compiler: CV & cover letter sharpening tool",
            COMMAND_COLORS["compile"],
        )

        mode_str: Optional[str] = "cv" if cv else ("cl" if cl else None)
        mode = _resolve_mode(mode_str)

        try:
            replacements, template, path = compile_with_data(
                mode=mode,
                username=username,
                verbose=verbose,
                seed_data=None,
            )
        except Exception as exc:
            typer.secho(f"Compilation failed: {exc}", fg="red")
            raise typer.Exit(1)

        typer.echo()
        typer.echo(
            typer.style("Compiled! ", fg=rgb_to_ansi(COMMAND_COLORS["compile"]), bold=True)
            + typer.style("see the PDF generated from: ", fg="white")
            + typer.style(f"{template.name}")
        )
        typer.echo()

        if typer.confirm(
            typer.style("Would you like to save this job info in CSV?", fg=rgb_to_ansi(COMMAND_COLORS["save"])),
            default=False,
        ):
            typer.echo(typer.style("Storing job info in CSV...", fg=rgb_to_ansi(COMMAND_COLORS["save"])))
            csv_path = save_job_in_csv(
                career=replacements["career"],
                job_position=replacements["job_position"],
                company_name=replacements["company_name"],
                location=replacements["location"],
                job_link=replacements["job_link"],
            )
            typer.echo(
                typer.style("Saved ", fg=rgb_to_ansi(COMMAND_COLORS["save"]), bold=True)
                + typer.style("Job info stored at: ", fg="white")
                + typer.style(f"{csv_path}_jobs.csv")
            )
            typer.echo()
        else:
            typer.echo(typer.style("Job info not saved in CSV.", fg=rgb_to_ansi(COMMAND_COLORS["save"])))
            typer.echo()
