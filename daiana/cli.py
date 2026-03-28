#!/usr/bin/env python
from typing import cast
import click


from daiana.commands.compiler_cli import register_compile_command
from daiana.commands.hunter_cli import register_hunt_command
from daiana.commands.oracler_cli import register_oracle_command
from daiana.commands.saver_cli import register_save_command
from daiana.commands.shower_cli import register_show_command
from daiana.commands.updater_cli import register_update_command
from daiana.utils.styles import *


class DaianaGroup(click.Group):
    def format_help(self, ctx, formatter) -> None:

        forest_teal = (0, 200, 120)
        light_wood = (200, 140, 100)
        banner_width = 60

        banner_top = click.style("╔" + "═"*(banner_width-2) + "╗", fg=forest_teal)
        banner_bot = click.style("╚" + "═"*(banner_width-2) + "╝", fg=forest_teal)

        # FIXED: Perfect daiana line
        bow_daiana_bow = "🏹 dAIana 🏹"
        daiana_spaces = (banner_width - 3 - len(bow_daiana_bow)) // 2
        daiana_line = f"{click.style("║", fg=light_wood)}{' ' * daiana_spaces}{click.style(bow_daiana_bow, fg=light_wood, bold=True)}{' ' * (daiana_spaces)}{click.style("║", fg=light_wood)}"
        banner_daiana = click.style(daiana_line, fg=forest_teal)

        # Goddess row
        goddess_line = f"║{center_text('AI assistant for Job Hunting', banner_width-2)}{' ' * (daiana_spaces-8)}║"
        banner_goddess = click.style(goddess_line, fg=light_wood)

        # Render
        click.echo()
        click.echo(banner_top)
        click.echo(banner_daiana)
        click.echo(banner_goddess)
        click.echo(banner_bot)
        click.echo()

        # Subtitles
        subtitle1 = "- Track & Update all your job applications -"
        subtitle2 = "- Compile CV & cover letter with AI help -"
        click.echo(click.style(center_text(subtitle1, banner_width), fg=light_wood))
        click.echo(click.style(center_text(subtitle2, banner_width), fg=light_wood))
        click.echo()

        # Commands header with bow
        click.echo(click.style("Hunt commands in this package:"))
        click.echo()
        # Colored commands list
        body = []
        for cmd_name in sorted(self.commands.keys()):
            color = COMMAND_COLORS.get(cmd_name, (240, 240, 240))
            cmd_label = get_command_color(cmd_name, color)
            cmd_help = self.commands[cmd_name].get_short_help_str(limit=80)
            body.append(f"  - {cmd_label}: {cmd_help}")
        # Render
        click.echo("\n".join(body))
        click.echo()


@DaianaGroup
def cli() -> None:
    """"""


for register in [
        register_compile_command,
        register_save_command,
        register_show_command,
        register_update_command,
        register_oracle_command,
        register_hunt_command
]:
    register(cli)


if __name__ == "__main__":
    cli()
