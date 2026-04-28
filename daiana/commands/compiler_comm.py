import typer

from rich.console import Console
from rich.text import Text

from daiana.core.compiler import compile_with_data
from daiana.core.saver import save_job_in_csv
from daiana.utils.for_latex import _resolve_mode
from daiana.utils.design.ui import DaianaUI, rgb
from daiana.utils.design.colors import COMMAND_COLORS

app = typer.Typer(
    help="Do you want to craft new weapons for your next hunt? Craft it!",
    no_args_is_help=True,
    rich_markup_mode="rich",
)

console = Console()
ui = DaianaUI()


@app.callback(invoke_without_command=True)
def compile(
    cv: bool = typer.Option(False, "--cv", help="CV mode."),
    cl: bool = typer.Option(False, "--cl", help="Cover letter mode."),
    username: str = typer.Option("user_name", "--username", "-un", help="Your name to appear in PDF name."),
    verbose: bool = typer.Option(False, "--verbose", help="Show LaTeX compilation information."),
) -> None:
    compile_color = COMMAND_COLORS["compile"]
    save_color = COMMAND_COLORS['save']

    console.print()
    ui.rule("dAIana compiler", color=compile_color)
    console.print()
    ui.info("[italic]CV & cover letter compiling tool[/italic]", color=compile_color)
    console.print()

    if cv and cl:
        console.print("[bold red]Choose only one mode: --cv or --cl[/bold red]")
        console.print()
        raise typer.Exit(code=1)

    mode = "cv" if cv else "cl" if cl else None
    mode = _resolve_mode(mode)

    try:
        replacements, template, path = compile_with_data(
            mode=mode,
            username=username,
            verbose=verbose,
            seed_data=None,
        )
    except Exception as exc:
        console.print(f"[bold red]Compilation failed: {exc}[/bold red]")
        console.print()
        raise typer.Exit(code=1)

    console.print()
    console.print(
        Text.assemble(
            ("Compiled! ", f"bold {rgb(compile_color)}"),
            ("See the PDF generated from: ", "white"),
            (f"{template.name}", "white"),
        )
    )
    console.print()

    should_save = typer.confirm(
        f"Would you like to save this job info in CSV?",
        default=False,
    )

    if should_save:
        console.print(f"[{rgb(save_color)}]Storing job info in CSV...[/{rgb(save_color)}]")

        csv_path = save_job_in_csv(
            career=replacements["career"],
            job_position=replacements["job_position"],
            company_name=replacements["company_name"],
            location=replacements["location"],
            job_link=replacements["job_link"],
        )

        console.print(
            Text.assemble(
                ("Saved ", f"bold {rgb(save_color)}"),
                ("Job info stored at: ", "white"),
                (f"{csv_path}_jobs.csv", "white"),
            )
        )
        console.print()
    else:
        console.print(f"Job info not [{rgb(save_color)}]saved[/{rgb(save_color)}] in CSV.")
        console.print()
