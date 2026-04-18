from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from rich import box
from rich.align import Align
from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text


COMMAND_COLORS: dict[str, tuple[int, int, int]] = {
    "save": (0, 200, 120),
    "update": (245, 200, 220),
    "show": (200, 140, 100),
    "hunt": (240, 60, 90),
    "oracle": (230, 190, 60),
    "compile": (30, 170, 240),
}

STATUS_COLORS: dict[str, tuple[int, int, int]] = {
    "applied": (240, 240, 240),
    "contacted": (250, 240, 180),
    "int_1": (150, 200, 150),
    "int_2": (70, 210, 190),
    "offered": (0, 200, 120),
    "rejected": (240, 60, 90),
}

NEUTRAL = (240, 240, 240)

FOREST_TEAL = (0, 200, 120)
LIGHT_WOOD = (200, 140, 100)
console = Console()


def rgb(color: tuple[int, int, int]) -> str:
    r, g, b = color
    return f"rgb({r},{g},{b})"


@dataclass(frozen=True)
class HelpCommand:
    name: str
    summary: str
    panel: str


class DaianaUI:
    def __init__(self) -> None:
        self.console = console

    def rule(self, title: str, color: tuple[int, int, int]) -> None:
        self.console.rule(
            f"[bold {rgb(color)}]{title}[/bold {rgb(color)}]",
            style=rgb(color),
            align="center",
        )

    def info(self, msg: str, color: tuple[int, int, int] = NEUTRAL) -> None:
        self.console.print(
            f"[italic {rgb(color)}]{msg}[/italic {rgb(color)}]",
            justify="center",
        )

    def item(self, msg: str, color: tuple[int, int, int] | None = None) -> None:
        style = rgb(color) if color else "white"
        self.console.print(f"  [{style}]{msg}[/{style}]")

    def success(self, msg: str, color: tuple[int, int, int]) -> None:
        self.console.print(f"[{rgb(color)}]✔[/{rgb(color)}] {msg}")

    def warning(self, msg: str, color: tuple[int, int, int]) -> None:
        self.console.print(f"[{rgb(color)}]⚠[/{rgb(color)}] {msg}")

    def error(self, msg: str, color: tuple[int, int, int]) -> None:
        self.console.print(f"[{rgb(color)}]✘[/{rgb(color)}] {msg}")

    def panel(self, msg: str, title: str, border_color: tuple[int, int, int]) -> None:
        renderable = Panel(
            msg,
            title=f"[bold {rgb(border_color)}]{title}[/bold {rgb(border_color)}]",
            title_align="center",
            border_style=rgb(border_color),
            padding=(1, 2),
            expand=False,
        )
        self.console.print(Align.center(renderable))

    def header(self, command: str) -> None:
        self.console.print()
        self.console.print(self.banner(command))
        self.console.print()

    def banner(self, command: str) -> Align:
        color = COMMAND_COLORS[command]
        subtitle = Text(
            "AI assistant for Job Hunting",
            style=f"italic {rgb(color)}",
            justify="center",
        )
        description = Text(
            "Track applications. Compile CV / cover letters with enhanced AI-guided workflows.",
            style=rgb(NEUTRAL),
            justify="center",
        )
        body = Group(subtitle, description)
        panel = Panel(
            body,
            border_style=rgb(color),
            padding=(1, 0),
            expand=False,
            title=f"[bold {rgb(color)}]dAIana[/bold {rgb(color)}]",
            title_align="center",
        )
        return Align.center(panel)

    def hero_help_panel(self) -> Align:
        hint = Text(
            "Job hunting tool empowered with AI cv & cover letter tailoring skills",
            style=f"italic {rgb(FOREST_TEAL)}",
            justify="center",
        )

        body = Group(
            hint,
        )

        panel = Panel(
            body,
            border_style=rgb(LIGHT_WOOD),
            padding=(0, 5),
            expand=False,
            title=f"[bold {rgb(LIGHT_WOOD)}]dAIana[/bold {rgb(LIGHT_WOOD)}]",
            title_align="center",
        )
        return Align.center(panel)

    def commands_table(self, commands: Iterable[HelpCommand]) -> Table:
        table = Table(
            box=box.SIMPLE_HEAVY,
            show_header=False,
            border_style=rgb(FOREST_TEAL),
            expand=True,
            pad_edge=False,
        )

        for cmd in commands:
            color = COMMAND_COLORS.get(cmd.name, NEUTRAL)
            table.add_row(
                f"[bold {rgb(color)}]{cmd.name}[/bold {rgb(color)}]",
                f"[white]{cmd.summary}[/white]",
            )
        return table

    def help_screen(self, commands: Iterable[HelpCommand]) -> None:
        self.console.print()
        self.console.print(self.hero_help_panel())
        self.console.print()

        commands_panel = Panel(
            self.commands_table(commands),
            title=f"[bold {LIGHT_WOOD}]Commands[/bold {LIGHT_WOOD}]",
            title_align="left",
            border_style=rgb(FOREST_TEAL),
            padding=(0, 0),
            expand=True,
        )
        self.console.print(Align.center(commands_panel))
        self.console.print()
