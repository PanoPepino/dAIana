"""Prompt file repository — replaces prompt_loader.py + prompts.py.

Prompt files are ONLY read when first accessed, never at import time.
This prevents startup crashes when DAIANA_JOB_HUNT_DIR is not set.
"""
from __future__ import annotations

import json
from pathlib import Path

import click


class PromptRepository:
    """Read and cache .md prompt files from a prompts/ directory."""

    def __init__(self, prompts_dir: Path) -> None:
        self._dir = prompts_dir
        self._cache: dict[str, str] = {}

    def text(self, name: str) -> str:
        """Return raw text of prompts/<name>.md, cached after first read."""
        if name not in self._cache:
            path = self._dir / f"{name}.md"
            if not path.exists():
                raise click.ClickException(f"Prompt file not found: {path}")
            self._cache[name] = path.read_text(encoding="utf-8")
        return self._cache[name]

    def as_json(self, name: str) -> dict | list:
        """Return parsed JSON from a prompt file."""
        return json.loads(self.text(name))

    def background_list(self) -> list[str]:
        """Parse bullet-point background items from background_payload."""
        raw = self.text("background/background_payload")
        return [
            line.lstrip("- ").strip()
            for line in raw.splitlines()
            if line.strip().startswith("-")
        ]

    def careers(self) -> list[str]:
        cfg = self.as_json("career/careers")
        return cfg["options"]

    def job_schema(self) -> dict:
        schema = self.as_json("job/job_schema")
        schema["career"] = "|".join(self.careers())
        return schema


def make_prompt_repository() -> PromptRepository:
    """Build a PromptRepository from the current runtime settings."""
    from daiana.config.settings import load_settings
    settings = load_settings()
    prompts_dir = settings.job_hunt_dir / "prompts"
    if not prompts_dir.exists():
        raise click.ClickException(f"Prompts directory not found: {prompts_dir}")
    return PromptRepository(prompts_dir)
