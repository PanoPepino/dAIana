from __future__ import annotations

import typer
from pathlib import Path
from rich.console import Console

from daiana.core.hunter import run_hunt_flow
from daiana.utils.design.ui import DaianaUI
from daiana.utils.design.colors import COMMAND_COLORS

app = typer.Typer(
    help="Ask guidance. Craft weapons. Track job preys. Hunt!",
    no_args_is_help=True,
    rich_markup_mode="rich",
)

ui = DaianaUI()
console = Console()


@app.callback(invoke_without_command=True)
def hunt(
    url: str = typer.Option(..., "-u", "--url", help="Job URL to scrape and parse as JSON oracle record."),
    csv_path: Path = typer.Option(
        Path("job_tracking"),
        "--csv-path",
        help="CSV file path reserved for existing daiana logic.",
    ),
    cv: bool = typer.Option(False, "--cv", help="Extract job information and compile your CV."),
    cl: bool = typer.Option(
        False, "--cl", help="Generate tailored cover-letter content and compile your cover letter."),
    username: str = typer.Option("user_name", "--username", "-un", help="Your name to appear in generated PDF names."),
    verbose: bool = typer.Option(False, "--verbose", help="Show LaTeX compilation details."),
) -> None:
    console.print('')
    ui.rule("dAIana hunt", color=COMMAND_COLORS['hunt'])
    console.print('')
    ui.info("[italic]Ask guidance. Choose weapons. Track. Hunt[/italic]", color=COMMAND_COLORS['hunt'])

    run_hunt_flow(
        url=url,
        csv_path=csv_path,
        cv=cv,
        cl=cl,
        username=username,
        verbose=verbose,
    )
    console.print('')
