"""Hunt service — replaces core/hunter.py."""
from __future__ import annotations

from pathlib import Path
from time import perf_counter

import typer
from rich.console import Console
from rich.text import Text

from daiana.services.compile_service import compile_with_data
from daiana.services.oracle_service import run_oracle_pipeline, edit_oracle_dict
from daiana.services.save_service import save_job_in_csv
from daiana.infra.filesystem import open_with_default_app
from daiana.utils.design.ui import rgb, _panel, _display_oracle_result
from daiana.utils.design.colors import COMMAND_COLORS
from daiana.utils.constants import NON_EDITABLE
import click

console = Console()
HUNT = COMMAND_COLORS["hunt"]
ORACLE = COMMAND_COLORS["oracle"]
COMPILE = COMMAND_COLORS["compile"]
SAVE = COMMAND_COLORS["save"]
UPDATE = COMMAND_COLORS["update"]


def _validate_hunt_mode(cv: bool, cl: bool) -> None:
    if not cv and not cl:
        raise click.ClickException("Use at least one flag: --cv and/or --cl")


def run_hunt_flow(url: str, csv_path: Path, cv: bool, cl: bool, username: str, verbose: bool) -> None:
    start = perf_counter()
    try:
        console.print()
        _validate_hunt_mode(cv, cl)

        extract = cv or cl
        select_projects = cv or cl
        select_background = cv or cl
        tailor_sentence = cl
        select_skills = cl
        path_cv = path_cl = None

        _show_hunt_intro(cv=cv, cl=cl)

        with console.status(f"[bold {rgb(ORACLE)}]Consulting oracle[/bold {rgb(ORACLE)}] ..."):
            result = run_oracle_pipeline(
                url=url, extract=extract, tailor_sentence=tailor_sentence,
                select_projects_flag=select_projects, select_background_flag=select_background,
                select_skills_flag=select_skills
            )

        if not isinstance(result, dict) or not result:
            console.print("[bold red]Oracle returned an empty result.[/bold red]")
            raise typer.Exit(code=1)

        console.print()
        _display_oracle_result(
            result=result, extract=extract, tailor_sentence=tailor_sentence,
            select_projects=select_projects, select_background=select_background,
            select_skills=select_skills
        )
        _maybe_edit_oracle_result(result)

        if cv:
            console.print()
            with console.status(f"[bold {rgb(COMPILE)}]Building CV[/bold {rgb(COMPILE)}] ..."):
                _, _, path_cv = compile_with_data(mode="cv", username=username, verbose=verbose, seed_data=result)
        if cl:
            with console.status(f"[bold {rgb(COMPILE)}]Building cover letter[/bold {rgb(COMPILE)}] ..."):
                _, _, path_cl = compile_with_data(mode="cl", username=username, verbose=verbose, seed_data=result)

        generated = [p for p in (path_cv, path_cl) if p]
        _maybe_open_pdfs(generated)
        _maybe_save_job(result)

    except (ValueError, typer.Exit):
        raise
    except Exception as exc:
        console.print(f"[bold red]Hunt failed: {exc}[/bold red]")
        raise typer.Exit(code=1) from exc
    finally:
        elapsed = perf_counter() - start
        console.print()
        console.print(f"[bold {rgb(HUNT)}]-- Finished in {elapsed:.2f}s --[/bold {rgb(HUNT)}]")
        console.print()


def _show_hunt_intro(cv: bool, cl: bool) -> None:
    if cv and cl:
        msg = "Extracting job information, crafting tailored sentence, choosing background and projects ..."
    elif cv:
        msg = "Extracting job info and selecting most relevant projects ..."
    else:
        msg = "Crafting tailored sentence, choosing background and projects ..."
    console.print(f"[bold {rgb(ORACLE)}]{msg}[/bold {rgb(ORACLE)}]")
    console.print()


def _maybe_edit_oracle_result(result: dict) -> None:
    editable = {k: v for k, v in result.items() if k not in NON_EDITABLE}
    if not editable:
        return
    console.print(f"Would you like to [{rgb(UPDATE)}]modify[/{rgb(UPDATE)}] this information?")
    if not typer.confirm("Modify fields", default=False):
        return
    updated = edit_oracle_dict(editable)
    result.update(updated)
    console.print()
    console.print(_panel(
        "Updated fields to send to compiler",
        [(f"{k}:", str(v)) for k, v in updated.items()],
        UPDATE,
    ))
    console.print()


def _maybe_open_pdfs(paths: list[Path]) -> None:
    if not paths:
        return
    console.print(f"Would you like to [{rgb(COMPILE)}]open[/{rgb(COMPILE)}] the PDF(s)?")
    if not typer.confirm("Open generated PDFs", default=False):
        return
    for p in paths:
        open_with_default_app(p)


def _maybe_save_job(result: dict) -> None:
    console.print(f"Would you like to [{rgb(SAVE)}]save[/{rgb(SAVE)}] this job info?")
    if not typer.confirm("Save job info", default=False):
        console.print(f"[{rgb(SAVE)}]Job info not saved.[/{rgb(SAVE)}]")
        return
    csv_path = save_job_in_csv(
        career=result["career"], job_position=result["job_position"],
        company_name=result["company_name"], location=result["location"], job_link=result["job_link"],
    )
    console.print(Text.assemble(
        ("Saved! ", f"bold {rgb(SAVE)}"),
        ("Job info stored at: ", "white"),
        (str(csv_path), "white"),
    ))
    console.print()
