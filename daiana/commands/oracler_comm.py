from __future__ import annotations

import typer

from rich.console import Console
from daiana.core.oracler import run_oracle_flow
from daiana.utils.ui import COMMAND_COLORS, DaianaUI

app = typer.Typer(
    help="Willing to get guidance from the AI oracle for next hunt? Ask it!",
    no_args_is_help=True,
    rich_markup_mode="rich",
)

ui = DaianaUI()
console = Console()


@app.callback(invoke_without_command=True)
def oracle(
    url: str = typer.Option(..., "-u", "--url", help="Job URL to scrape and parse."),
    csv_path: str = typer.Option(
        "job_tracking",
        "--csv-path",
        help="CSV file path reserved for existing daiana logic.",
    ),
    extract: bool = typer.Option(False, "--extract", help="Extract structured job metadata."),
    tailor_sentence: bool = typer.Option(False, "--tailor_sentence",
                                         help="Generate tailored background + challenge slots for the cover letter."),
    select_projects: bool = typer.Option(False, "--select_projects",
                                         help="Select the 3 most relevant CV projects for this job posting."),
    select_background: bool = typer.Option(False, "--select_background",
                                           help="Select the 3 most relevant background skills for the cover letter."),
) -> None:
    console.print('')
    ui.rule("dAIana oracle", color=COMMAND_COLORS['oracle'])
    console.print('')
    ui.info("[italic]Ask guidance to the Oracle[/italic]", color=COMMAND_COLORS['oracle'])
    run_oracle_flow(
        url=url,
        csv_path=csv_path,
        extract=extract,
        tailor_sentence=tailor_sentence,
        select_projects=select_projects,
        select_background=select_background,
    )
    console.print('')
