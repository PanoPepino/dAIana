"""
The most important file, as it gathers the full logic and aim of this package. It first calls the oracler, this extracts all required information for the job. Then, it will allow you to modify the information with updater. After that, it will send everything to the compiler and finally, will add the information about your application in the corresponding csv with saver.py!
"""

from __future__ import annotations

import typer

from pathlib import Path
from time import perf_counter
from rich.console import Console
from rich.text import Text

from daiana.core.compiler import compile_with_data
from daiana.core.oracler import run_oracle_pipeline
from daiana.core.saver import save_job_in_csv
from daiana.utils.for_hunt import _validate_hunt_mode, open_with_default_app
from daiana.utils.for_oracle import edit_oracle_dict
from daiana.utils.design.ui import rgb, _panel
from daiana.core.oracler import _display_oracle_result
from daiana.utils.design.colors import COMMAND_COLORS
from daiana.utils.constants import NON_EDITABLE


console = Console()

HUNT = COMMAND_COLORS['hunt']
ORACLE = COMMAND_COLORS['oracle']
COMPILE = COMMAND_COLORS["compile"]
SAVE = COMMAND_COLORS['save']
UPDATE = COMMAND_COLORS['update']


def run_hunt_flow(
    url: str,
    csv_path: Path,
    cv: bool,
    cl: bool,
    username: str,
    verbose: bool,
) -> None:
    start = perf_counter()

    try:
        console.print()
        _validate_hunt_mode(cv, cl)

        extract = cv or cl
        select_projects = cv or cl
        select_background = cv or cl
        tailor_sentence = cl

        path_cv = None
        path_cl = None

        _show_hunt_intro(cv=cv, cl=cl)

        with console.status(f"[bold {rgb(ORACLE)}]Consulting oracle[/bold {rgb(ORACLE)}] ..."):
            result = run_oracle_pipeline(
                url=url,
                extract=extract,
                tailor_sentence=tailor_sentence,
                select_projects=select_projects,
                select_background=select_background,
            )

        if not isinstance(result, dict):
            console.print("[bold red]Oracle pipeline did not return a dictionary.[/bold red]")
            raise typer.Exit(code=1)

        if not result:
            console.print("[bold red]Oracle returned an empty result.[/bold red]")
            raise typer.Exit(code=1)

        console.print()
        _display_oracle_result(
            result=result,
            extract=extract,
            tailor_sentence=tailor_sentence,
            select_projects=select_projects,
            select_background=select_background,
        )

        _maybe_edit_oracle_result(result)

        if cv:
            console.print()
            with console.status(f"[bold {rgb(COMPILE)}]Building CV[/bold {rgb(COMPILE)}] ..."):
                _, _, path_cv = compile_with_data(
                    mode="cv",
                    username=username,
                    verbose=verbose,
                    seed_data=result,
                )
            console.print()

        if cl:
            with console.status(f"[bold {rgb(COMPILE)}]Building cover letter[/bold {rgb(COMPILE)}] ..."):
                _, _, path_cl = compile_with_data(
                    mode="cl",
                    username=username,
                    verbose=verbose,
                    seed_data=result,
                )
            console.print()

        generated_paths = [p for p in (path_cv, path_cl) if p is not None]
        _maybe_open_pdfs(generated_paths)
        _maybe_save_job(result)

    except ValueError as exc:
        console.print(f"[bold red]{exc}[/bold red]")
        raise typer.Exit(code=1) from exc
    except typer.Exit:
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
        message = (
            "Extracting job information, crafting tailored sentence, "
            "choosing best background skills and relevant projects ..."
        )
    elif cv:
        message = "Extracting information of your next trophy and selecting most relevant projects ..."
    else:
        message = "Crafting tailored sentence, choosing best background skills and relevant projects ..."

    console.print(f"[bold {rgb(ORACLE)}]{message}[/bold {rgb(ORACLE)}]")
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
    console.print(
        _panel(
            "Updated fields to send to compiler",
            [(f"{key}:", str(value)) for key, value in updated.items()],
            UPDATE,
        )
    )
    console.print()


def _maybe_open_pdfs(generated_paths: list[Path]) -> None:
    if not generated_paths:
        return

    console.print(f"Would you like to [{rgb(COMPILE)}]open[/{rgb(COMPILE)}] the tailored PDF(s)?")
    if not typer.confirm("Open generated PDFs", default=False):
        return

    for pdf_path in generated_paths:
        open_with_default_app(pdf_path)
    console.print()


def _maybe_save_job(result: dict) -> None:
    console.print(f"Would you like to [{rgb(SAVE)}]save[/{rgb(SAVE)}] this job info in CSV?")
    should_save = typer.confirm("Save job info", default=False)

    if should_save:
        csv_path = save_job_in_csv(
            career=result["career"],
            job_position=result["job_position"],
            company_name=result["company_name"],
            location=result["location"],
            job_link=result["job_link"],
        )
        console.print(
            Text.assemble(
                ("Saved! ", f"bold {rgb(SAVE)}"),
                ("Job info stored at: ", "white"),
                (f"{csv_path}_jobs.csv", "white"),
            )
        )
        console.print()
    else:
        console.print(f"[{rgb(SAVE)}]Job info not saved in CSV.[/{rgb(SAVE)}]")
        console.print()
