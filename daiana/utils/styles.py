from daiana.utils.constants import STATUS_COLORS, ALLOW_STATUS, COMMAND_COLORS
from typing import Dict
import click


class DaianaCommand(click.Command):
    """
    Custom Click Command subclass that:
    - Colors the help description line using the command's COMMAND_COLORS entry.
    - Adds a blank line after the last option before the terminal prompt.
    """

    def format_help(self, ctx: click.Context, formatter: click.HelpFormatter) -> None:
        # Resolve command color (fallback to white)
        color = COMMAND_COLORS.get(self.name, (240, 240, 240))
        click.echo()
        # Color the description
        if self.help:
            click.echo(click.style(self.help, fg=color, bold=True))
            click.echo()

        # Render Usage + Options normally via formatter
        # self.format_usage(ctx, formatter)
        self.format_options(ctx, formatter)


def get_status_color(action: str) -> Dict[str, any]:
    """
    Simple function to map a color to its associated status and/or date.
    """
    coloring = STATUS_COLORS.get(action.lower(), "white")
    return {"fg": coloring}


def get_command_color(command: str, color: str) -> str:
    """
    Simple function to map a color to its associated command.
    """
    return click.style(command, fg=color)


def center_text(text: str, width: int) -> str:
    """Center text within given width."""
    spaces = (width - len(text)) // 2
    return " " * spaces + text


def command_banner(title: str, cmd_color: tuple,
                   banner_width: int = 60) -> None:
    """
    Single-line compact Diana banner.
    """
    top_left, horiz, top_right = "┌", "─", "┐"
    bot_left, bot_right = "└", "┘"

    box_top = click.style(top_left + horiz*(banner_width-2) + top_right, fg=cmd_color)
    box_bot = click.style(bot_left + horiz*(banner_width-2) + bot_right, fg=cmd_color)

    title_spaces = (banner_width - 2 - len(title)) // 2
    title_line = f"|{' ' * title_spaces}{click.style(title, bold=True)}{' ' * title_spaces}{click.style('|', fg=cmd_color)}"
    box_title = click.style(title_line, fg=cmd_color)

    click.echo()
    click.echo(box_top)
    click.echo(box_title)
    click.echo(box_bot)
    click.echo()
