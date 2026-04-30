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
from daiana.utils.design.colors import *


console = Console()

# Keys that must never be printed as raw text.
_SKILLS_LATEX_KEY = "selected_skills_latex"
_SKILL_DISPLAY_SLOTS: frozenset[str] = frozenset(
    key
    for i in range(1, 5)
    for key in (f"_skill_cat_{i}", f"_skill_items_{i}")
)
_HIDDEN_KEYS: frozenset[str] = _SKILL_DISPLAY_SLOTS | {_SKILLS_LATEX_KEY}


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
            "Let dAIana enhance your job hunt.",
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
            "Ask the Oracle. Sharp your weapons. Track down. Hunt your dreamt jobs.",
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


def _panel(title: str, items: list[tuple[str, str]], color) -> Panel:
    if isinstance(color, tuple) and len(color) == 3:
        color_style = f"rgb({color[0]},{color[1]},{color[2]})"
    else:
        color_style = str(color)

    return Panel(
        _field_table(items),
        title=f"[bold {color_style}]{title}[/bold {color_style}]",
        title_align="left",
        border_style=color_style,
        padding=(1, 2),
        expand=False,
    )


def _skills_panel(data: dict, color_style: str) -> Panel | None:
    """Build a skills panel from _skill_cat_N / _skill_items_N keys in *data*.

    Returns None when no skill slots are present so callers can guard easily.
    """
    rows: list[tuple[str, str]] = []
    for i in range(1, 5):
        cat = str(data.get(f"_skill_cat_{i}", "")).strip()
        items = str(data.get(f"_skill_items_{i}", "")).strip()
        if cat:
            rows.append((f"{i}. {cat}:", items or "-"))

    if not rows:
        return None

    return _panel(
        "Selected skills (ranked by relevance)",
        rows,
        color=color_style,
    )


def _display_oracle_result(
    result: dict,
    extract: bool,
    tailor_sentence: bool,
    select_projects: bool,
    select_background: bool,
    select_skills: bool = False,
) -> None:
    """
    Display all information collected by oracle commands as structured panels.
    """
    oracle_color = rgb(COMMAND_COLORS["oracle"])

    if extract:
        console.print(_panel(
            "Extracted data",
            [
                ("job_position:", result.get("job_position", "")),
                ("company_name:", result.get("company_name", "")),
                ("career:", result.get("career", "")),
                ("location:", result.get("location", "")),
                ("job_link:", result.get("job_link", "")),
            ],
            color=oracle_color,
        ))
        console.print()

    if tailor_sentence or select_background:
        console.print(_panel(
            "Background skills and tailored sentence",
            [
                ("sentence_first_paragraph:", result.get("sentence_first_paragraph", "")),
                ("your_background:", result.get("your_background", "")),
            ],
            color=oracle_color,
        ))
        console.print()

    if select_projects:
        projects_panel = _panel(
            "Selected projects",
            [
                ("project_one:", result.get("project_one", "")),
                ("project_two:", result.get("project_two", "")),
                ("project_three:", result.get("project_three", "")),
            ],
            color=oracle_color,
        )

        reasons_text = []
        for i, proj_key in enumerate(["project_one", "project_two", "project_three"], 1):
            proj_name = result.get(proj_key, "")
            reason = result.get(f"reason_selected_{i}", "-")
            reasons_text.append(f"{proj_name}: {reason}")

        reasons_panel = _panel(
            "Reasons for choosing those projects",
            [("", "\n\n".join(reasons_text))],
            color=oracle_color,
        )

        console.print(
            Columns([projects_panel, reasons_panel], equal=True, expand=True)
        )
        console.print()

    if tailor_sentence:
        console.print(_panel(
            "Extra material (not included in documents)",
            [
                ("challenge_area:", result.get("challenge_area", "")),
                ("business_domain:", result.get("business_domain", "")),
            ],
            color=oracle_color,
        ))
        console.print()

    if select_skills:
        panel = _skills_panel(result, oracle_color)
        if panel is not None:
            console.print(panel)
            console.print()


def _display_updated_fields(updated: dict) -> None:
    """
    Display modified fields after the interactive updater.

    Skill display slots (_skill_cat_N / _skill_items_N) and the raw LaTeX key
    are suppressed from the flat list and rendered as a panel instead.
    """
    update_color = rgb(COMMAND_COLORS["update"])

    plain_items = [
        (f"{key}:", str(value))
        for key, value in updated.items()
        if key not in _HIDDEN_KEYS
    ]

    has_skill_updates = bool(_SKILL_DISPLAY_SLOTS & set(updated))

    if plain_items:
        console.print()
        console.print(_panel("Updated fields", plain_items, color=update_color))
        console.print()

    if has_skill_updates:
        panel = _skills_panel(updated, update_color)
        if panel is not None:
            console.print(panel)
            console.print()


def _show_active_modes(
    extract: bool,
    tailor_sentence: bool,
    select_projects: bool,
    select_background: bool,
    select_skills: bool = False,
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
    if select_skills:
        active.append("selecting and ranking relevant skills")

    console.print()

    return active
