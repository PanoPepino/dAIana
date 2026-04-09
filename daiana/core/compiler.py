import click
import subprocess
import shutil
import os
import tempfile

from typing import Optional
from pathlib import Path

from daiana.utils.for_latex import (
    check_pdflatex,
    detect_project_root,
    build_texinputs,
    read_log,
    extract_errors,
    get_mode_config,
    _ask_for_missing
)
from daiana.utils.for_csv import rewrite_filename
from daiana.utils.constants import COMMAND_COLORS


def _collect_compile_data(mode: str, seed_data: dict | None = None) -> dict:
    """
    This is the first important function that will ask for inputs in case missing fields when the oracler seeds information.

    Args:
        mode (str): cv or cl flags from hunt mode of daiana.
        seed_data (dict | None, optional): If oracle mode has been invoked first, it will just ask entries not passed from oracle to compile

    Returns:
        dict: The complete dictionary to pass to latex.
    """

    seed_data = seed_data or {}

    click.echo(click.style("In case of missing fields, please, fill these in: ", fg=COMMAND_COLORS["compile"]))
    click.echo()

    resolved = {}
    resolved["career"] = _ask_for_missing("career", "1) Career", seed_data)
    resolved["job_position"] = _ask_for_missing("job_position", "2) Job Position", seed_data)
    resolved["company_name"] = _ask_for_missing("company_name", "3) Company Name", seed_data)
    resolved["location"] = _ask_for_missing("location", "4) Job Location", seed_data, default="")
    resolved["job_link"] = _ask_for_missing("job_link", "5) Job Link", seed_data, default="")

    if mode == "cl":
        resolved["your_background"] = _ask_for_missing(
            "your_background",
            "6) Your tailored background",
            seed_data,
        )
        resolved["sentence_first_paragraph"] = _ask_for_missing(
            "sentence_first_paragraph",
            "7) The company's challenge(s)",
            seed_data,
        )
        resolved["project_one"] = _ask_for_missing(
            "project_one",
            "8) First relevant project",
            seed_data,
        )
        resolved["project_two"] = _ask_for_missing(
            "project_two",
            "9) Second relevant project",
            seed_data,
        )

    if mode == "cv":
        resolved["project_one"] = _ask_for_missing(
            "project_one",
            "6) First relevant project",
            seed_data,
        )
        resolved["project_two"] = _ask_for_missing(
            "project_two",
            "7) Second relevant project",
            seed_data,
        )
        resolved["project_three"] = _ask_for_missing(
            "project_three",
            "8) Last relevant project",
            seed_data,
        )

    return resolved


def build_replacements(mode: str, data: dict) -> dict:
    """
    This function will eat inputs from terminal (or the the dict spit out by :func:`_collect_compile_data`) and spit out the final dictionary with the right commands to substitute in latex files.

    Args:
        mode (str): Depending on the document to pass
        data (dict): The information to be substituted in the latex file.

    Returns:
        dict: The information to be substituted in the latex file.
    """

    # config = get_mode_config(mode)

    replacements = {
        "career": data.get("career", ""),
        "job_position": data.get("job_position", ""),
        "company_name": data.get("company_name", ""),
        "location": data.get("location", ""),
        "job_link": data.get("job_link", ""),
    }

    if mode == "cl":
        replacements.update(
            {
                "your_background": data.get("your_background", ""),
                "sentence_first_paragraph": data.get("sentence_first_paragraph", ""),
                "cp_latex": f"\\body{replacements['career']}" if replacements["career"] else "",
                "project_one": f"\\{data.get("project_one", "")}",
                "project_two": f"\\{data.get("project_two", "")}",
            }
        )

    if mode == "cv":
        replacements.update(
            {
                "project_one": f"\\{data.get("project_one", "")}",
                "project_two": f"\\{data.get("project_two", "")}",
                "project_three": f"\\{data.get("project_three", "")}",
            }
        )

    return replacements


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


def compile_tex(
        tex_file: Path,
        relative_output_dir: Optional[Path] = None,
        clean: bool = True,
        texinputs: Optional[str] = None,
        project_root: Optional[Path] = None,
        verbose: bool = False,
        silent: bool = True,
        passes: int = 2) -> Path:
    """
    This function will compile the previous modified and copied .tex file to PDF using pdflatex.

    Raises:
        click.ClickException: if pdflatex is missing, the tex file is missing, or no PDF is produced.

    Returns:
        Path: the path to the generated PDF.
    """

    if not check_pdflatex():
        raise click.ClickException("pdflatex not found.")

    tex_path = tex_file.absolute()
    if not tex_path.exists():
        raise click.ClickException(f"TeX file not found: {tex_path}")

    stem = tex_path.stem
    root = Path(project_root).absolute() if project_root else detect_project_root(tex_path)
    if relative_output_dir is None:
        relative_output_dir = 'output'
    pdf_path = root / relative_output_dir / f"{stem}.pdf"

    with tempfile.TemporaryDirectory(prefix="daiana-") as tmp_str:
        tmp_root = Path(tmp_str)

        for item in root.iterdir():
            dest = tmp_root / item.name
            if item.is_file():
                shutil.copy2(item, dest)
            elif item.is_dir():
                shutil.copytree(item, dest, dirs_exist_ok=True)

        rel_tex = tex_path.relative_to(root)
        tmp_tex = tmp_root / rel_tex
        tmp_tex_dir = tmp_tex.parent
        log_path = tmp_tex_dir / f"{stem}.log"

        env = os.environ.copy()
        env["TEXINPUTS"] = texinputs if texinputs else build_texinputs(tmp_root)

        cmd = [
            "pdflatex",
            "-interaction=batchmode",
            "-halt-on-error",
            str(tmp_tex)
        ]

        for i in range(passes):
            if silent:
                result = subprocess.run(
                    cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    cwd=tmp_tex_dir,
                    env=env
                )
            else:
                result = subprocess.run(cmd, capture_output=False, cwd=tmp_tex_dir, env=env)

            if verbose:
                log_text = read_log(log_path)
                click.echo(f"\U0001f4cb Pass {i+1}/{passes}:", err=True)
                click.echo(extract_errors(log_text)[-500:], err=True)
            elif not silent and result.returncode != 0:
                log_text = read_log(log_path)
                click.secho(f"\u26a0 Pass {i+1}/{passes} failed", fg="red", err=True)
                click.echo(extract_errors(log_text), err=True)
            elif not silent:
                click.echo(f"\u2713 Pass {i+1}/{passes}")

        tmp_pdf = tmp_tex_dir / f"{stem}.pdf"
        if not tmp_pdf.exists():
            if verbose:
                log_text = read_log(log_path)
                click.echo(f"\n\u274c No PDF. Log:\n{log_text}")
            raise click.ClickException("No PDF produced.")

        shutil.move(tmp_pdf, pdf_path)

        if clean:
            for ext in [".aux", ".log", ".fls", ".fdb_latexmk", ".synctex.gz", ".out", ".tex"]:
                f = tmp_tex_dir / f"{stem}{ext}"
                if f.exists():
                    f.unlink()
            if tex_path.exists():
                tex_path.unlink()

    if not silent:
        click.echo(f"\u2713 {pdf_path}")
    return pdf_path


def render_and_compile(mode: str,
                       username: str,
                       replacements: dict,
                       verbose: bool = False):
    """
    This function will make use of the duplicated and the dictionary to pass and will compile the the desired.tex file and generate .PDF.
    """

    config = get_mode_config(mode)

    to_feed = render_template(
        config["template"],
        replacements,
        stem_replacement=f"{username}_{config['addon_name']}",
    )
    path = compile_tex(to_feed, verbose=verbose)
    return config["template"], path


def compile_with_data(
    *,
    mode: str,
    username: str,
    verbose: bool,
    seed_data: dict | None = None,
):
    """
    This function summarises all previous functions into one single pipeline.
    """
    replacements = _collect_compile_data(mode, seed_data)
    replacements = build_replacements(mode, replacements)
    template, path = render_and_compile(
        mode=mode,
        username=username,
        replacements=replacements,
        verbose=verbose,
    )
    return replacements, template, path
