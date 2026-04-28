import typer

from daiana.core.initer import copy_directory_func, set_env_func
from daiana.utils.for_init import check_api_environment

app = typer.Typer(invoke_without_command=True)


@app.callback()
def init(
    copy_directory: bool = typer.Option(
        False,
        "--copy_directory",
        help="Copy the local job_hunt folder to a new location.",
    ),
    set_env: bool = typer.Option(
        False,
        "--set_env",
        help="Ask for provider, model, base URL, API key name, and API key value, then save them in the project .env.",
    ),
    check_env: bool = typer.Option(
        False,
        "--check_env",
        help="Check the environment selected, test the API service, and return a simple oracle test.",
    ),
) -> None:
    if copy_directory:
        copy_directory_func()
        raise typer.Exit()

    if set_env:
        set_env_func()
        raise typer.Exit()

    if check_env:
        check_api_environment()
        raise typer.Exit()

    typer.echo("Use one of: --copy_directory, --set_env, --check_env")
