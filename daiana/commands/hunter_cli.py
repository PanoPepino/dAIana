import click
import os
import platform
import subprocess

from pathlib import Path
from time import perf_counter
from daiana.core.oracler import run_oracle_pipeline
from daiana.core.compiler import compile_with_data
from daiana.core.saver import save_job_in_csv
from daiana.utils.for_oracle import edit_oracle_dict
from daiana.utils.styles import DaianaCommand, command_banner, COMMAND_COLORS


def register_hunt_command(cli: click.Group) -> None:
    @cli.command("hunt", cls=DaianaCommand, help="Ask AI, choose skills, compile documents & track job.")
    @click.option("-u", "--url", required=True, help="Job URL to scrape and parse as JSON oracle record.")
    @click.option(
        "--csv-path",
        type=click.Path(path_type=Path),
        default=Path("job_tracking"),
        show_default=True,
        help="CSV file path reserved for existing daiana logic.",
    )
    @click.option(
        "--cv",
        is_flag=True,
        help="Extract job information and compile your CV.",
    )
    @click.option(
        "--cl",
        is_flag=True,
        help="Generate tailored cover-letter content and compile your cover letter.",
    )
    @click.option(
        "--username",
        "-un",
        default="user_name",
        help="Your name to appear in generated PDF names.",
    )
    @click.option(
        "--verbose",
        is_flag=True,
        help="Show LaTeX compilation details.",
    )
    def hunt_job(url: str, csv_path: Path, cv: bool, cl: bool, username: str, verbose: bool) -> None:
        start = perf_counter()

        command_banner(
            "dAIana hunt: Ask guidance. Choose weapons. Track. Hunt",
            COMMAND_COLORS["hunt"],
        )

        click.echo()

        _validate_hunt_mode(cv, cl)

        extract = cv or cl
        tailor_cl = cl

        path_cv = None
        path_cl = None

        try:
            if cv and cl:
                click.secho(
                    "Extracting job information and crafting tailored sentence(s) ...",
                    fg=COMMAND_COLORS["oracle"],
                )
            elif cv:
                click.secho(
                    "Extracting information of your next trophy ...",
                    fg=COMMAND_COLORS["oracle"],
                )
            else:
                click.secho(
                    "Tailoring your requested sentence(s) ...",
                    fg=COMMAND_COLORS["oracle"],
                )

            click.echo()

            result = run_oracle_pipeline(
                url=url,
                extract=extract,
                tailor_cl=tailor_cl,
            )

            if not isinstance(result, dict):
                raise click.ClickException("Oracle pipeline did not return a dictionary.")

            if not result:
                raise click.ClickException("Oracle returned an empty result.")

            _print_result_block("Oracle result:", result, COMMAND_COLORS["oracle"])

            if click.confirm(
                click.style("Would you like to modify this information?", fg=COMMAND_COLORS["update"]),
                default=False,
            ):
                click.echo()
                result = edit_oracle_dict(result)
                _print_result_block("The new fields are:", result, COMMAND_COLORS["update"])

            if cv:
                click.echo()
                click.secho("Compiling CV ...", fg=COMMAND_COLORS["compile"])
                re_cv, temp_cv, path_cv = compile_with_data(
                    mode="cv",
                    username=username,
                    verbose=verbose,
                    seed_data=result,
                )
                click.echo()

            if cl:
                click.secho("Compiling cover letter ...", fg=COMMAND_COLORS["compile"])
                re_cl, temp_cl, path_cl = compile_with_data(
                    mode="cl",
                    username=username,
                    verbose=verbose,
                    seed_data=result,
                )
                click.echo()

            generated_paths = [p for p in (path_cv, path_cl) if p is not None]

            if generated_paths and click.confirm(
                click.style("Would you like to open the tailored PDF(s)?", fg=COMMAND_COLORS["compile"]),
                default=False,
            ):
                for pdf_path in generated_paths:
                    open_with_default_app(pdf_path)
                click.echo()

            if click.confirm(
                click.style("Would you like to save this job info in CSV?", fg=COMMAND_COLORS["save"]),
                default=False,
            ):
                click.echo(click.style("Storing job info in CSV...", fg=COMMAND_COLORS["save"]))
                csv_path = save_job_in_csv(
                    career=result["career"],
                    job_position=result["job_position"],
                    company_name=result["company_name"],
                    location=result["location"],
                    job_link=result["job_link"],
                )
                click.echo(
                    click.style("Saved ", fg=COMMAND_COLORS["save"], bold=True)
                    + click.style("Job info stored at: ", fg="white")
                    + click.style(f"{csv_path}_jobs.csv")
                )
                click.echo()
            else:
                click.echo(click.style("Job info not saved in CSV.", fg=COMMAND_COLORS["save"]))
                click.echo()

        except ValueError as exc:
            raise click.ClickException(str(exc)) from exc
        except Exception as exc:
            raise click.ClickException(f"Hunt failed: {exc}") from exc
        finally:
            elapsed = perf_counter() - start
            click.secho(f" -- Finished in {elapsed:.2f}s --")
            click.echo()


def _validate_hunt_mode(cv: bool, cl: bool) -> None:
    if not cv and not cl:
        raise click.ClickException("Use at least one flag: --cv and/or --cl")


def _print_result_block(title: str, data: dict, color: str) -> None:
    click.secho(title, fg=color)
    click.echo()
    for key, value in data.items():
        click.echo(f"{key:17}: {value}")
    click.echo()


def open_with_default_app(path: Path) -> None:
    path = Path(path).expanduser().resolve()

    if not path.exists():
        raise click.ClickException(f"Cannot open missing file: {path}")

    system_name = platform.system()

    try:
        if system_name == "Windows":
            os.startfile(path)  # type: ignore[attr-defined]
        elif system_name == "Darwin":
            subprocess.run(["open", str(path)], check=True)
        else:
            subprocess.run(["xdg-open", str(path)], check=True)
    except Exception as exc:
        raise click.ClickException(f"Could not open file with default viewer: {path}") from exc
