import typer
import os
import platform
import subprocess

from pathlib import Path
from time import perf_counter
from daiana.core.oracler import run_oracle_pipeline
from daiana.core.compiler import compile_with_data
from daiana.core.saver import save_job_in_csv
from daiana.utils.for_oracle import edit_oracle_dict
from daiana.utils.styles import command_banner, rgb_to_ansi
from daiana.utils.constants import COMMAND_COLORS


def register_hunt_command(app: typer.Typer) -> None:
    @app.command("hunt", help="Ask AI, choose skills, compile documents & track job.")
    def hunt_job(
        url:      str  = typer.Option(..., "-u", "--url",     help="Job URL to scrape and parse."),
        csv_path: Path = typer.Option(Path("job_tracking"), "--csv-path", show_default=True, help="CSV file path."),
        cv:       bool = typer.Option(False, "--cv",          help="Extract job information and compile your CV."),
        cl:       bool = typer.Option(False, "--cl",          help="Generate tailored cover-letter content and compile."),
        username: str  = typer.Option("user_name", "--username", "-un", help="Your name for PDF filenames."),
        verbose:  bool = typer.Option(False, "--verbose",     help="Show LaTeX compilation details."),
    ) -> None:
        start = perf_counter()
        command_banner("dAIana hunt: Ask guidance. Choose weapons. Track. Hunt", COMMAND_COLORS["hunt"])
        typer.echo()

        _validate_hunt_mode(cv, cl)

        extract   = cv or cl
        tailor_cl = cl
        path_cv = path_cl = None

        try:
            if cv and cl:
                typer.secho("Extracting job information and crafting tailored sentence(s) ...", fg=rgb_to_ansi(COMMAND_COLORS["oracle"]))
            elif cv:
                typer.secho("Extracting information of your next trophy ...", fg=rgb_to_ansi(COMMAND_COLORS["oracle"]))
            else:
                typer.secho("Tailoring your requested sentence(s) ...", fg=rgb_to_ansi(COMMAND_COLORS["oracle"]))

            typer.echo()

            result = run_oracle_pipeline(url=url, extract=extract, tailor_cl=tailor_cl)

            if not isinstance(result, dict) or not result:
                typer.secho("Oracle pipeline did not return a valid dictionary.", fg="red")
                raise typer.Exit(1)

            _print_result_block("Oracle result:", result, COMMAND_COLORS["oracle"])

            if typer.confirm(
                typer.style("Would you like to modify this information?", fg=rgb_to_ansi(COMMAND_COLORS["update"])),
                default=False,
            ):
                typer.echo()
                result = edit_oracle_dict(result)
                _print_result_block("The new fields are:", result, COMMAND_COLORS["update"])

            if cv:
                typer.echo()
                typer.secho("Compiling CV ...", fg=rgb_to_ansi(COMMAND_COLORS["compile"]))
                _, _, path_cv = compile_with_data(mode="cv", username=username, verbose=verbose, seed_data=result)
                typer.echo()

            if cl:
                typer.secho("Compiling cover letter ...", fg=rgb_to_ansi(COMMAND_COLORS["compile"]))
                _, _, path_cl = compile_with_data(mode="cl", username=username, verbose=verbose, seed_data=result)
                typer.echo()

            generated_paths = [p for p in (path_cv, path_cl) if p is not None]

            if generated_paths and typer.confirm(
                typer.style("Would you like to open the tailored PDF(s)?", fg=rgb_to_ansi(COMMAND_COLORS["compile"])),
                default=False,
            ):
                for pdf_path in generated_paths:
                    open_with_default_app(pdf_path)
                typer.echo()

            if typer.confirm(
                typer.style("Would you like to save this job info in CSV?", fg=rgb_to_ansi(COMMAND_COLORS["save"])),
                default=False,
            ):
                typer.echo(typer.style("Storing job info in CSV...", fg=rgb_to_ansi(COMMAND_COLORS["save"])))
                csv_path = save_job_in_csv(
                    career=result["career"],
                    job_position=result["job_position"],
                    company_name=result["company_name"],
                    location=result["location"],
                    job_link=result["job_link"],
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

        except ValueError as exc:
            typer.secho(str(exc), fg="red")
            raise typer.Exit(1)
        except Exception as exc:
            typer.secho(f"Hunt failed: {exc}", fg="red")
            raise typer.Exit(1)
        finally:
            elapsed = perf_counter() - start
            typer.secho(f" -- Finished in {elapsed:.2f}s --")
            typer.echo()


def _validate_hunt_mode(cv: bool, cl: bool) -> None:
    if not cv and not cl:
        typer.secho("Use at least one flag: --cv and/or --cl", fg="red")
        raise typer.Exit(1)


def _print_result_block(title: str, data: dict, color) -> None:
    typer.secho(title, fg=rgb_to_ansi(color))
    typer.echo()
    for key, value in data.items():
        typer.echo(f"{key:17}: {value}")
    typer.echo()


def open_with_default_app(path: Path) -> None:
    path = Path(path).expanduser().resolve()
    if not path.exists():
        typer.secho(f"Cannot open missing file: {path}", fg="red")
        raise typer.Exit(1)
    system_name = platform.system()
    try:
        if system_name == "Windows":
            os.startfile(path)  # type: ignore[attr-defined]
        elif system_name == "Darwin":
            subprocess.run(["open", str(path)], check=True)
        else:
            subprocess.run(["xdg-open", str(path)], check=True)
    except Exception as exc:
        typer.secho(f"Could not open file with default viewer: {path}\n{exc}", fg="red")
        raise typer.Exit(1)
