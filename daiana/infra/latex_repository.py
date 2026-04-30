"""LaTeX compilation helpers — replaces utils/for_latex.py."""
from __future__ import annotations

import os
import re
import shutil
from pathlib import Path

import click
import typer

from daiana.utils.constants import MODE_CONFIG


# ── LaTeX text escaping ─────────────────────────────────────────────────────

# Ordered so that backslash is handled first, preventing double-escaping.
_LATEX_SPECIAL: list[tuple[str, str]] = [
    ("\\", r"\textbackslash{}"),
    ("&",  r"\&"),
    ("%",  r"\%"),
    ("$",  r"\$"),
    ("#",  r"\#"),
    ("_",  r"\_"),
    ("{",  r"\{"),
    ("}",  r"\}"),
    ("~",  r"\textasciitilde{}"),
    ("^",  r"\textasciicircum{}"),
]


def latex_escape(text: str) -> str:
    """Escape all LaTeX special characters in a plain-text string.

    Safe to call on category labels and any other text that must not
    contain raw LaTeX control sequences.  Do NOT call on strings that
    already contain intentional LaTeX markup (e.g. item lists with
    \\textbf{...} — use escape_bare_ampersands() for those instead).
    """
    for char, replacement in _LATEX_SPECIAL:
        text = text.replace(char, replacement)
    return text


def escape_bare_ampersands(text: str) -> str:
    """Escape only unescaped & characters in a string that may already
    contain other LaTeX markup (e.g. skill item lists).

    Matches & not preceded by a backslash.
    """
    return re.sub(r"(?<!\\)&", r"\\&", text)


# ── pdflatex helpers ─────────────────────────────────────────────────────────

def check_pdflatex() -> bool:
    return shutil.which("pdflatex") is not None


def detect_project_root(tex_file: Path) -> Path:
    for candidate in [tex_file.parent, *tex_file.parent.parents]:
        if (candidate / "cls").exists() or (candidate / "loader").exists():
            return candidate
    return tex_file.parent


def build_texinputs(tmp_root: Path) -> str:
    paths = ["./"]
    cls_dir = tmp_root / "cls"
    if cls_dir.exists() and any(cls_dir.glob("*.cls")):
        paths.append(f"{tmp_root / 'cls'}//")
    paths.append(f"{tmp_root / 'loader'}//")
    prefix = ":".join(paths) + ":"
    return prefix + os.environ.get("TEXINPUTS", "")


def read_log(log_path: Path) -> str:
    return log_path.read_text(errors="replace") if log_path.exists() else "(no log file found)"


def extract_errors(log_text: str) -> str:
    lines = log_text.splitlines()
    relevant = [
        ln for ln in lines
        if any(tag in ln for tag in ["! ", "Error", "Warning", "LaTeX Error", "Undefined"])
    ]
    return "\n".join(relevant) if relevant else "(no errors found in log)"


def get_mode_config(mode: str) -> dict:
    if mode not in MODE_CONFIG:
        raise ValueError("Use mode='cv' or mode='cl'")
    return MODE_CONFIG[mode]


def ask_for_missing(field_name: str, label: str, data: dict, default: str = "") -> str:
    value = data.get(field_name)
    if value not in (None, ""):
        return value
    return typer.prompt(label, default=default, show_default=bool(default))


def resolve_mode(mode: str | None) -> str:
    if mode not in {"cv", "cl"}:
        raise click.ClickException("Use exactly one mode: --cv or --cl")
    return mode
