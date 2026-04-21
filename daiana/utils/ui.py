from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from rich import box
from rich.align import Align
from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.columns import Columns
from daiana.utils.colors import *


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


def _field_table(items: list[tuple[str, str]]) -> Table:
    """
    General function to add columns to a table.
    """
    table = Table.grid(padding=(0, 1))
    table.add_column(style="white", no_wrap=True)
    table.add_column(style="white")

    for label, value in items:
        table.add_row(f"[bold white]{label}[/bold white]", value or "-")

    return table


def _panel(
    title: str,
    items: list[tuple[str, str]],
    color: tuple[int, int, int],
) -> Panel:
    """
    Function that calls :func: `_field_table` and creates a table inside a panel
    """
    return Panel(
        _field_table(items),
        title=f"[bold {color}]{title}[/bold {color}]",
        title_align="left",
        border_style=color,
        padding=(1, 2),
        expand=False,
    )


def _display_oracle_result(
    result: dict,
    extract: bool,
    tailor_sentence: bool,
    select_projects: bool,
    select_background: bool,
) -> None:
    """
    Function to display all information collected by oracle commands in the form of well structured panels.
    """
    if extract:
        console.print(_panel(
            "Extracted data",
            [
                ("job_position:", result.get("job_position", "")),
                ("company_name:", result.get("company_name", "")),
                ("career:", result.get("career", "")),
                ("location:", result.get("location", "")),
                ("job_link:", result.get("job_link", "")),
            ], color=rgb(COMMAND_COLORS['oracle'])))
        console.print()

    if tailor_sentence or select_background:
        console.print(_panel(
            "Background skills and tailored sentence",
            [
                ("sentence_first_paragraph:", result.get("sentence_first_paragraph", "")),
                ("your_background:", result.get("your_background", "")),
            ], color=rgb(COMMAND_COLORS['oracle'])))
        console.print()

    if select_projects:
        projects_panel = _panel(
            "Selected projects",
            [
                ("project_one:", result.get("project_one", "")),
                ("project_two:", result.get("project_two", "")),
                ("project_three:", result.get("project_three", "")),
            ],
            color=rgb(COMMAND_COLORS['oracle']),
        )

        reasons_text = []
        for i, proj_key in enumerate(["project_one", "project_two", "project_three"], 1):
            proj_name = result.get(proj_key, "")
            reason_key = f"reason_name_{i}"
            reason = result.get(reason_key, "-")
            reasons_text.append(f"{proj_name}: {reason}")

        reasons_panel = _panel(
            "Reasons for choosing those projects",
            [("reasons:", "\n".join(reasons_text))],
            color=rgb(COMMAND_COLORS['oracle']),
        )

        console.print(
            Columns(
                [projects_panel, reasons_panel],
                equal=True,
                expand=True,
            )
        )
        console.print()

    if tailor_sentence:
        console.print(_panel(
            "Extra material (not included in documents)",
            [
                ("challenge_area:", result.get("challenge_area", "")),
                ("business_domain:", result.get("business_domain", "")),
            ],
            color=rgb(COMMAND_COLORS['oracle'])))
        console.print()


def _display_updated_fields(updated: dict) -> None:
    """
    Function to display in a simple panel any information modified with updater.
    """
    items = [(f"{key}:", str(value)) for key, value in updated.items()]
    console.print()
    console.print(_panel("Updated fields", items, color=rgb(COMMAND_COLORS['update'])))
    console.print()


def _show_active_modes(
    extract: bool,
    tailor_sentence: bool,
    select_projects: bool,
    select_background: bool,
) -> list[str]:
    active: list[str] = []

    if extract:
        active.append("extracting job metadata")
    if tailor_sentence:
        active.append("tailoring cover letter slots")
    if select_projects:
        active.append("selecting relevant projects")
    if select_background:
        active.append("selecting relevant background skills")

    console.print()

    return active
