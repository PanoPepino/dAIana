from __future__ import annotations

from pathlib import Path
import typer

from daiana.commands import init_comm
from daiana.utils.design.ui import DaianaUI, HelpCommand


app = typer.Typer(
    help="dAIana CLI for job hunting, CV compilation, and AI-guided workflows.",
    add_completion=False,
    rich_markup_mode="rich",
    no_args_is_help=False,
    context_settings={"help_option_names": ["-h", "--help"]},
)

ui = DaianaUI()


@app.callback(invoke_without_command=True)
def root(
    ctx: typer.Context,
    job_hunt_dir: Path | None = typer.Option(
        None,
        "--job-hunt-dir",
        help="Path to the external job_hunt directory.",
        envvar="DAIANA_JOB_HUNT_DIR",
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        resolve_path=True,
    ),
) -> None:
    ctx.ensure_object(dict)
    ctx.obj["job_hunt_dir"] = job_hunt_dir

    if ctx.invoked_subcommand is not None:
        return

    commands = [
        HelpCommand(name="init", summary="Prepare your set up to start hunting jobs!", panel="init"),
        HelpCommand(name="show", summary="Do you want to see your latest hunt trophies? Show it!", panel="show"),
        HelpCommand(name="save", summary="A new job hunt trophy to add to the records? Add it!", panel="save"),
        HelpCommand(name="update", summary="Information to be updated for your latest prey? Update it!", panel="update"),
        HelpCommand(
            name="compile", summary="Do you want to craft new weapons, cv and cover letter, for your next hunt? Craft it!", panel="compile"),
        HelpCommand(name="oracle", summary="Willing to get guidance from the AI oracle for next hunt? Ask it!", panel="oracle"),
        HelpCommand(name="hunt", summary="Ask guidance. Craft weapons. Track job preys. Hunt!", panel="hunt"),
    ]

    ui.help_screen(commands)
    raise typer.Exit()


app.add_typer(
    init_comm.app,
    name="init",
    help="Prepare your set up to start hunting jobs!",
)


def register_other_commands() -> None:
    from daiana.commands import (
        compiler_comm,
        hunter_comm,
        oracler_comm,
        saver_comm,
        shower_comm,
        updater_comm,
    )

    app.add_typer(shower_comm.app, name="show", help="Do you want to see your latest hunt trophies? Show it!")
    app.add_typer(saver_comm.app, name="save", help="A new job hunt trophy to add to the records? Add it!")
    app.add_typer(updater_comm.app, name="update", help="Information to be updated for your latest prey? Update it!")
    app.add_typer(compiler_comm.app, name="compile",
                  help="Do you want to craft new weapons for your next hunt? Craft it!")
    app.add_typer(oracler_comm.app, name="oracle",
                  help="Willing to get guidance from the AI oracle for next hunt? Ask it!")
    app.add_typer(hunter_comm.app, name="hunt", help="Ask guidance. Craft weapons. Track job preys. Hunt!")


register_other_commands()


def main() -> None:
    app()


if __name__ == "__main__":
    main()
