"""DEBUG: Live regex testing."""

import re
from pathlib import Path
import click

from daiana.allowed import STATUS_COLORS


def latex_escape(text):
    replacements = {'&': r'\&', '%': r'\%', '$': r'\$', '_': r'\_', '{': r'\{', '}': r'\}', '\\': r'\textbackslash{}'}
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text


def replace_newcommand(tex_content, command_name, new_value, escape=True):
    print(f"\n🔍 DEBUG replace_newcommand:")
    print(f"  Command: {command_name}")
    print(f"  Old value target: {new_value}")

    if escape:
        new_value = latex_escape(new_value)
        print(f"  Escaped new: {repr(new_value)}")

    # BULLETPROOF PATTERN
    pattern = r'\\newcommand\{\\' + re.escape(command_name) + r'\}\{(.*?)\}\}'
    print(f"  Pattern: {repr(pattern)}")

    # Find matches
    matches = re.findall(pattern, tex_content, re.DOTALL)
    print(f"  Found {len(matches)} matches: {matches[:2]}")

    # Replace
    result = re.sub(pattern, rf'\\newcommand{{\\{command_name}}}{{{new_value}}}', tex_content, flags=re.DOTALL)

    old_count = len(re.findall(r'\\newcommand\{\\' + re.escape(command_name) + r'\}', tex_content))
    new_count = len(re.findall(r'\\newcommand\{\\' + re.escape(command_name) + r'\}', result))
    print(f"  Old commands: {old_count}, New: {new_count}")

    return result


def read_tex_file(file_path):
    return Path(file_path).read_text(encoding='utf-8')


def write_tex_file(file_path, content):
    Path(file_path).write_text(content, encoding='utf-8')


def rewrite_filename(name: str) -> str:

    name = name.strip().lower()
    # Replace any sequence of non-alphanumeric characters with underscore
    name = re.sub(r"[^a-z0-9]+", "_", name)
    # Remove leading/trailing underscores
    name = name.strip("_")
    return name or "default"


def check_dir_exist() -> Path:
    """
    This function checks if a given folder exists. If not, creates it.

    Returns:
        Path: the current direction / job_tracking.
    """

    original_dir = Path.cwd()
    data_dir = original_dir/'job_tracking'
    data_dir.mkdir(exist_ok=True)
    return data_dir


def history_formatter(history: str) -> str:

    parts = [p.strip() for p in history.split("|") if p.strip()]
    colored_pieces = []

    for part in parts:

        status, date = part.split(":", 1)
        status = status.strip()
        date = date.strip()

        color = STATUS_COLORS.get(status, 'white')
        colored_date = click.style(date, fg=color)
        colored_pieces.append(f"{colored_date}")

    return click.style(" | ", fg='magenta').join(colored_pieces)
