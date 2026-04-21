import shutil
import subprocess
import sys
import os
import click
import typer

from pathlib import Path

from daiana.utils.constants import MODE_CONFIG


def check_pdflatex() -> bool:
    return shutil.which("pdflatex") is not None


def detect_project_root(tex_file: Path) -> Path:
    for candidate in [tex_file.parent, *tex_file.parent.parents]:
        if (candidate / "cls").exists() or (candidate / "loader").exists():
            return candidate
    return tex_file.parent


def build_texinputs(tmp_root: Path) -> str:
    paths = ["./"]

    cls_dir = tmp_root / 'cls'
    if cls_dir.exists() and any(cls_dir.glob('*.cls')):
        paths.append(f"{tmp_root / 'cls'}//")

    paths.append(f"{tmp_root / 'loader'}//")

    prefix = ":".join(paths) + ":"
    original = os.environ.get("TEXINPUTS", "")
    return prefix + original


def read_log(log_path: Path) -> str:
    if log_path.exists():
        return log_path.read_text(errors="replace")
    return "(no log file found)"


def extract_errors(log_text: str) -> str:
    lines = log_text.splitlines()
    relevant = [l for l in lines if any(
        tag in l for tag in ["! ", "Error", "Warning", "LaTeX Error", "Undefined"]
    )]
    return "\n".join(relevant) if relevant else "(no errors found in log)"


def get_mode_config(mode: str) -> dict:
    if mode not in MODE_CONFIG:
        raise ValueError("Use mode='cv' or mode='cl'")
    return MODE_CONFIG[mode]


def _ask_for_missing(field_name: str,
                     label: str,
                     data: dict,
                     default: str = "") -> str:
    value = data.get(field_name)
    if value not in (None, ""):
        return value

    return typer.prompt(
        label,
        default=default,
        show_default=bool(default),
    )


def _resolve_mode(mode: str | None) -> str:
    if mode not in {"cv", "cl"}:
        raise click.ClickException("Use exactly one mode: --cv or --cl")
    return mode
