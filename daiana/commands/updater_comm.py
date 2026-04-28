import typer

from rich.console import Console

from daiana.utils.design.ui import DaianaUI
from daiana.utils.for_update import run_update_flow
from daiana.utils.design.colors import COMMAND_COLORS

app = typer.Typer(
    help="Information to be updated for your latest prey? Update it!",
    no_args_is_help=True,
    rich_markup_mode="rich",
)

ui = DaianaUI()
console = Console()


@app.callback(invoke_without_command=True)
def update(
    career: str = typer.Option(..., "--career", "-cp", help='Career path, e.g. "data".'),
    status: bool = typer.Option(False, "--status", "-s", help="Update application status."),
    field: bool = typer.Option(False, "--field", "-f", help="Edit any non-status field."),
    erase: bool = typer.Option(False, "--erase", "-e", help="Erase a stored row."),
) -> None:
    console.print("")
    ui.rule("dAIana updater", color=COMMAND_COLORS['update'])
    console.print("")
    ui.info("[italic]Update or erase a job application[/italic]", color=COMMAND_COLORS['update'])

    run_update_flow(
        career=career,
        status=status,
        field=field,
        erase=erase,
    )
    console.print("")
