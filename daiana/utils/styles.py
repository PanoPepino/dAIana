from daiana.utils.constants import STATUS_COLORS, ALLOW_STATUS, COMMAND_COLORS
from typing import Dict
import click


def get_status_color(action: str) -> Dict[str, any]:
    """
    Simple function to map a color to its associated status and/or date.

    Args:
        action (str): The status of the history in the json file.

    Returns:
        Dict[str, any]: The appropiate color for the status.
    """

    coloring = STATUS_COLORS.get(action.lower(), "white")
    return {"fg": coloring}


def get_command_color(command: str,
                      color: str) -> str:
    """
    Simple function to map a color to its associated command.

    Args:
        command (str): The status of the history in the json file.

    Returns:
        str: The appropiate color for the comand.
    """

    return click.style(command, fg=color)


def center_text(text: str, width: int) -> str:
    """Center text within given width."""
    spaces = (width - len(text)) // 2
    return " " * spaces + text


def command_banner(title: str, cmd_color: tuple,
                   banner_width: int = 60) -> None:
    """
    Single‑line compact Diana banner
    """

    # Single line symbols
    top_left, horiz, top_right = "┌", "─", "┐"
    bot_left, bot_right = "└", "┘"

    # Box (60 cols)
    box_top = click.style(top_left + horiz*(banner_width-2) + top_right, fg=cmd_color)
    box_bot = click.style(bot_left + horiz*(banner_width-2) + bot_right, fg=cmd_color)

    # Centered bold title
    title_spaces = (banner_width - 2 - len(title)) // 2
    title_line = f"|{' ' * title_spaces}{click.style(title, bold=True)}{' ' * title_spaces}{click.style('|', fg=cmd_color)}"
    box_title = click.style(title_line, fg=cmd_color)

    click.echo()
    click.echo(box_top)
    click.echo(box_title)
    click.echo(box_bot)
    click.echo()
