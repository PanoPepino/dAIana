"""Cross-platform filesystem helpers."""
from __future__ import annotations

import os
import platform
import subprocess
from pathlib import Path

import click


def open_with_default_app(path: Path) -> None:
    path = Path(path).expanduser().resolve()
    if not path.exists():
        raise click.ClickException(f"Cannot open missing file: {path}")
    system_name = platform.system()
    try:
        if system_name == "Windows":
            os.startfile(path)  # type: ignore[attr-defined]
        elif system_name == "Darwin":
            subprocess.run(["open", str(path)], check=True)
        else:
            subprocess.run(["xdg-open", str(path)], check=True)
    except Exception as exc:
        raise click.ClickException(f"Could not open file: {path}") from exc
