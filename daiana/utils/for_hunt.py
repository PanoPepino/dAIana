import click
import os
import platform
import subprocess

from pathlib import Path


def _validate_hunt_mode(cv: bool, cl: bool) -> None:
    if not cv and not cl:
        raise click.ClickException("Use at least one flag: --cv and/or --cl")


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
        raise click.ClickException(f"Could not open file with default viewer: {path}") from exc
