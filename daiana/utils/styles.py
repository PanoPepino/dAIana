import typer
from typing import Dict
from daiana.utils.constants import STATUS_COLORS, COMMAND_COLORS

# ── Colour helpers ──────────────────────────────────────────────────────────
# Typer/Click accept named ANSI colours as strings.
# The original code stored colours as RGB tuples; we keep that dict here so
# callers are unchanged, but we map them to nearest ANSI names for output.

_RGB_TO_ANSI: dict[tuple[int, int, int], str] = {
    (0, 200, 120):   "bright_green",   # forest_teal  → banner border
    (200, 140, 100): "yellow",          # light_wood   → banner text
    (180, 220, 255): "bright_cyan",     # compile
    (255, 180, 100): "bright_yellow",   # save
    (140, 200, 140): "green",           # show
    (200, 150, 255): "bright_magenta",  # update
    (255, 220, 100): "yellow",          # oracle
    (100, 200, 255): "cyan",            # hunt
}


def rgb_to_ansi(color: tuple | str) -> str:
    """Convert an RGB tuple to the nearest ANSI colour name Typer understands."""
    if isinstance(color, str):
        return color
    return _RGB_TO_ANSI.get(color, "white")


def get_status_color(action: str) -> Dict[str, str]:
    """
    Simple function to map a color to its associated status and/or date.
    """
    coloring = STATUS_COLORS.get(action.lower(), "white")
    return {"fg": coloring}


def get_command_color(command: str, color: tuple | str) -> str:
    """
    Simple function to map a color to its associated command.
    """
    return typer.style(command, fg=rgb_to_ansi(color), bold=True)


def center_text(text: str, width: int) -> str:
    """Center text within given width."""
    spaces = (width - len(text)) // 2
    return " " * spaces + text


def command_banner(title: str, cmd_color: tuple | str,
                   banner_width: int = 60) -> None:
    """
    Single-line compact Daiana banner using Typer styling.
    """
    ansi = rgb_to_ansi(cmd_color)
    top_left, horiz, top_right = "\u250c", "\u2500", "\u2510"
    bot_left, bot_right = "\u2514", "\u2518"

    box_top = typer.style(top_left + horiz * (banner_width - 2) + top_right, fg=ansi)
    box_bot = typer.style(bot_left + horiz * (banner_width - 2) + bot_right, fg=ansi)

    title_spaces = (banner_width - 2 - len(title)) // 2
    title_line = (
        typer.style("|", fg=ansi)
        + " " * title_spaces
        + typer.style(title, bold=True)
        + " " * title_spaces
        + typer.style("|", fg=ansi)
    )

    typer.echo()
    typer.echo(box_top)
    typer.echo(title_line)
    typer.echo(box_bot)
    typer.echo()
