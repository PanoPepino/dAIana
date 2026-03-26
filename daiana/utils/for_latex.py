import shutil
import subprocess
import sys
import os
from pathlib import Path

from daiana.utils.for_csv import rewrite_filename


def render_template(template_path: Path,
                    replacements: dict[str, str],
                    stem_replacement: str = None) -> Path:
    """
    This function will create a copy of the chosen template, with a prepared name to be easily identified after compiled.

    Args:
        template_path (Path): The template you wanna compile.
        replacements (dict[str, str]): The dic of strings to replace in the template \\newcommands.
        stem_replacement (str, optional): To be substituted in future. Basically, it changes the name of the copy template for easier identification when output

    Returns:
        Path: The absolute(?) path where the copied and modified template is at. (temporal file)
    """

    directory_obj, obj_to_copy = template_path.parent, template_path.stem
    company_pos_ending = rewrite_filename(replacements['company_name'].lower())
    if stem_replacement:
        fake_template = f"{stem_replacement}_{company_pos_ending}"
    else:
        fake_template = f"{obj_to_copy}_{company_pos_ending}"
    new_path = Path(f"{directory_obj}/{fake_template}.tex")

    shutil.copy2(template_path, new_path)
    text = new_path.read_text(encoding="utf-8")
    for placeholder, value in replacements.items():
        text = text.replace(f"{placeholder}", value)
    new_path.write_text(text, encoding="utf-8")
    return new_path


def open_pdf(pdf_path):
    """Open PDF in default system viewer."""
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    if sys.platform == "darwin":  # macOS
        subprocess.run(["open", str(pdf_path)])
    elif sys.platform == "win32":  # Windows
        os.startfile(str(pdf_path))
    else:  # Linux and others
        subprocess.run(["xdg-open", str(pdf_path)])
