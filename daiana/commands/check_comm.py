from __future__ import annotations

import typer
from rich.console import Console

from daiana.services.check_service import check_prompt
from daiana.utils.design.ui import DaianaUI, _panel
from daiana.utils.design.colors import COMMAND_COLORS
from daiana.utils.for_check import check_api

app = typer.Typer(
    help="Check environment settings and prompt files before hunting.",
    no_args_is_help=True,
    rich_markup_mode="rich",
)

ui = DaianaUI()
console = Console()


@app.callback(invoke_without_command=True)
def check(
    env: bool = typer.Option(
        False,
        "--env",
        help="Check the loaded environment and test the oracle connection.",
    ),
    prompts: bool = typer.Option(
        False,
        "--prompts",
        help="Load and inspect all prompt assets used by the oracle.",
    ),
) -> None:

    console.print()
    ui.rule("dAIana check", color=COMMAND_COLORS["check"])
    console.print()
    ui.info("[italic]Inspect prompts and environment before the next hunt[/italic]", color=COMMAND_COLORS["check"])
    console.print()

    if not env and not prompts:
        typer.echo("Use at least one flag: --env or --prompts")
        raise typer.Exit(code=1)

    if env:
        checks = check_api()
        table_items = [(key, str(value)) for key, value in checks.items()]
        console.print(_panel("Current API", table_items, color=COMMAND_COLORS['check']))

        console.print()

    if prompts:
        check_prompt()
