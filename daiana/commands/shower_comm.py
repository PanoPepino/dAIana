import typer

from rich.console import Console
from rich.text import Text
from daiana.core.shower import get_last_jobs
from daiana.utils.design.styles import jobs_table, status_legend
from daiana.utils.design.ui import DaianaUI, rgb
from daiana.utils.design.colors import COMMAND_COLORS

app = typer.Typer(
    help="Inspect previous applied jobs and their status.",
    no_args_is_help=True,
    rich_markup_mode="rich",
)

console = Console()
ui = DaianaUI()


@app.callback(invoke_without_command=True)
def show(
    career: str = typer.Option(..., "--career", "-cp", help='Career path, e.g. "data".'),
    rows: int = typer.Option(20, "--rows", "-rj", min=1, help="Number of recent jobs to display."),
) -> None:
    console.print()
    ui.rule("dAIana show", color=COMMAND_COLORS['show'])
    console.print()

    ui.info(f"[italic] Inspect previous hunting trophies[/italic]", color=COMMAND_COLORS['show'])
    console.print()
    try:
        rows_data, csv_path, total_rows = get_last_jobs(career, rows)
    except FileNotFoundError as exc:
        console.print(f"[bold red]{exc}[/bold red]")
        raise typer.Exit(code=1)

    if not rows_data:
        console.print("[bold yellow]No jobs saved yet for this career path.[/bold yellow]")
        raise typer.Exit()

    console.print(jobs_table(rows_data))
    console.print()
    console.print(status_legend())
    console.print()
    console.print(
        Text.assemble(
            ("Showing ", rgb(COMMAND_COLORS['show'])),
            (f"last {len(rows_data)} job(s) ", f"bold {rgb(COMMAND_COLORS['show'])}"),
            ("from ", "white"),
            (str(csv_path), "white"),
        )
    )
    console.print('')
    console.print(
        Text.assemble(
            ("Total # of applications: ", rgb(COMMAND_COLORS['show'])),
            (f"{total_rows}"),
        )
    )
    console.print()
