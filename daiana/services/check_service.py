from __future__ import annotations

import os

import typer
from rich.console import Console

import daiana.utils.prompts as prompts
from daiana.utils.prompt_loader import loader
from daiana.utils.design.colors import COMMAND_COLORS
from daiana.utils.design.ui import _panel

console = Console()


def _describe_value(name: str, value) -> tuple[str, str]:
    if isinstance(value, str):
        preview = value[:80].replace("\n", " ")
        return name, f"{len(value)} chars | '{preview}...'"
    if isinstance(value, list):
        first = value[0] if value else ""
        return name, f"{len(value)} items | first: '{first}'"
    if isinstance(value, dict):
        keys = list(value.keys())
        return name, f"{len(keys)} keys | {keys}"
    return name, f"unexpected type {type(value)}"


def check_prompt() -> None:
    color = COMMAND_COLORS["check"]

    diagnostics = [
        ("DAIANA_JOB_HUNT_DIR", os.getenv("DAIANA_JOB_HUNT_DIR", "<not set>")),
        ("Prompts dir", str(loader.prompts_dir)),
    ]

    console.print(_panel("Prompt loader diagnostic", diagnostics, color=color))
    console.print()

    core_prompts = [
        _describe_value("JOB_PROMPT", prompts.JOB_PROMPT),
        _describe_value("SENTENCE_PROMPT", prompts.SENTENCE_PROMPT),
        _describe_value("PROJECTS_PROMPT", prompts.PROJECTS_PROMPT),
        _describe_value("BACKGROUND_PROMPT", prompts.BACKGROUND_PROMPT),
    ]

    payloads = [
        _describe_value("PROJECTS_PAYLOAD", prompts.PROJECTS_PAYLOAD),
        _describe_value("BACKGROUND_PAYLOAD", prompts.BACKGROUND_PAYLOAD),
        _describe_value("BACKGROUND (parsed list)", prompts.BACKGROUND),
    ]

    schemas = [
        _describe_value("SENTENCE_SCHEMA", prompts.SENTENCE_SCHEMA),
        _describe_value("JOB_SCHEMA", prompts.JOB_SCHEMA),
        _describe_value("PROJECTS_SCHEMA", prompts.PROJECTS_SCHEMA),
        _describe_value("BACKGROUND_SCHEMA", prompts.BACKGROUND_SCHEMA),
        _describe_value("PROJECT_NAME_TO_LATEX", prompts.PROJECT_NAME_TO_LATEX),
    ]

    console.print(_panel("Core prompts", core_prompts, color=color))
    console.print()
    console.print(_panel("Payloads", payloads, color=color))
    console.print()
    console.print(_panel("Schemas and mappings", schemas, color=color))
    console.print()

    console.print("[bold green]Prompts successfully loaded[/bold green]")

    console.print()
