#!/usr/bin/env python
import typer

from daiana.commands.compiler_cli import register_compile_command
from daiana.commands.hunter_cli   import register_hunt_command
from daiana.commands.oracler_cli  import register_oracle_command
from daiana.commands.saver_cli    import register_save_command
from daiana.commands.shower_cli   import register_show_command
from daiana.commands.updater_cli  import register_update_command
from daiana.utils.styles import center_text, get_command_color, rgb_to_ansi
from daiana.utils.constants import COMMAND_COLORS

app = typer.Typer(
    name="daiana",
    help="\U0001f3f9 dAIana \U0001f3f9 — AI assistant for Job Hunting",
    add_completion=False,
    invoke_without_command=True,
)


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context) -> None:
    """Print the dAIana banner when no subcommand is given."""
    if ctx.invoked_subcommand is None:
        forest_teal = "bright_green"
        light_wood  = "yellow"
        width = 60

        border = typer.style("+" + "-" * (width - 2) + "+", fg=forest_teal)
        title_text = "\U0001f3f9 dAIana \U0001f3f9"
        spaces = (width - 3 - len(title_text)) // 2
        title_line = (
            typer.style("|", fg=light_wood)
            + " " * spaces
            + typer.style(title_text, fg=light_wood, bold=True)
            + " " * spaces
            + typer.style("|", fg=light_wood)
        )
        sub_line = typer.style(
            f"| {center_text('AI assistant for Job Hunting', width - 2)}              |",
            fg=light_wood,
        )

        typer.echo()
        typer.echo(border)
        typer.echo(title_line)
        typer.echo(sub_line)
        typer.echo(border)
        typer.echo()

        typer.echo(typer.style(center_text("- Track & Update all your job applications -", width), fg=light_wood))
        typer.echo(typer.style(center_text("- Compile CV & cover letter with AI help -",   width), fg=light_wood))
        typer.echo()
        typer.echo(typer.style("Hunt commands in this package:"))
        typer.echo()

        for cmd_info in sorted(app.registered_commands, key=lambda c: c.name or ""):
            color     = COMMAND_COLORS.get(cmd_info.name or "", (240, 240, 240))
            label     = get_command_color(cmd_info.name or "", color)
            help_text = (cmd_info.callback.__doc__ or "").strip() if cmd_info.callback else ""
            typer.echo(f"  - {label}: {help_text}")


# Register all sub-commands
for _register in [
    register_compile_command,
    register_save_command,
    register_show_command,
    register_update_command,
    register_oracle_command,
    register_hunt_command,
]:
    _register(app)


if __name__ == "__main__":
    app()
