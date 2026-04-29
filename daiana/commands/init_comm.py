import typer
from rich.console import Console
from daiana.core.initer import copy_directory_func, set_env_func
from daiana.utils.design.ui import DaianaUI
from daiana.utils.design.colors import COMMAND_COLORS


ui = DaianaUI()
app = typer.Typer(invoke_without_command=True)
console = Console()


@app.callback()
def init(
    copy_directory: bool = typer.Option(
        False,
        "--copy_dir",
        help="Copy the local job_hunt folder to a new location.",
    ),
    set_env: bool = typer.Option(
        False,
        "--set_env",
        help="Ask for provider, model, base URL, API key name, and API key value, then save them in the project .env.",
    ),
) -> None:
    console.print('')
    ui.rule("dAIana init", color=COMMAND_COLORS['init'])
    console.print('')
    ui.info("[italic]Set your hunting armory. Configure the shrine for the Oracle[/italic]", color=COMMAND_COLORS['init'])
    console.print("")

    if copy_directory:
        copy_directory_func()
        raise typer.Exit()

    if set_env:
        set_env_func()
        raise typer.Exit()

    ui.info("[italic]Use one of: --copy_dir or --set_env[/italic]", color=COMMAND_COLORS['init'])
