import typer

from rich.console import Console
from rich.text import Text

from daiana.core.saver import save_job_in_csv
from daiana.utils.ui import COMMAND_COLORS, DaianaUI, rgb

app = typer.Typer(
    help="A new job hunt trophy to add to the records? Add it!",
    no_args_is_help=True,
    rich_markup_mode="rich",
)

console = Console()
ui = DaianaUI()


@app.callback(invoke_without_command=True)
def save(
    career: str = typer.Option(..., "--career", "-cp", help='Career path, e.g. "software".'),
) -> None:
    save_color = COMMAND_COLORS["save"]

    console.print()
    ui.rule("dAIana saver", color=save_color)
    console.print()

    ui.info(f"[italic] Save your latest preys[/italic]", color=COMMAND_COLORS["save"])
    console.print()

    console.print(f"[{rgb(save_color)}]Fill in the fields below:[/{rgb(save_color)}]")
    console.print()

    job_position = typer.prompt("1) Job position ")
    company_name = typer.prompt("2) Company name")
    location = typer.prompt("3) Location", default="", show_default=False)
    job_link = typer.prompt(
        "4) Link to job description (press ENTER if none)",
        default="",
        show_default=False,
    )
    console.print()

    csv_path = save_job_in_csv(
        career=career,
        job_position=job_position,
        company_name=company_name,
        location=location,
        job_link=job_link,
    )

    console.print(
        Text.assemble(
            ("Saved ", f"bold {rgb(save_color)}"),
            ("Job info stored at: ", "white"),
            (f"{csv_path}_jobs.csv", "white"),
        )
    )
    console.print()
