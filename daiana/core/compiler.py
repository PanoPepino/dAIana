import click
import subprocess
import shutil
import os
import tempfile

from typing import Optional
from pathlib import Path
from daiana.utils.for_latex import render_template
from daiana.utils.constants import MODE_CONFIG, COMMAND_COLORS


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
    Compile a .tex file to PDF using pdflatex.

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


def get_mode_config(mode: str) -> dict:
    if mode not in MODE_CONFIG:
        raise ValueError("Use mode='cv' or mode='cl'")
    return MODE_CONFIG[mode]


def build_replacements(mode: str, data: dict) -> dict:
    config = get_mode_config(mode)

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
            }
        )

    return replacements


def render_and_compile(mode: str, username: str, replacements: dict, verbose: bool = False):
    config = get_mode_config(mode)

    to_feed = render_template(
        config["template"],
        replacements,
        stem_replacement=f"{username}_{config['addon_name']}",
    )
    path = compile_tex(to_feed, verbose=verbose)
    return config["template"], path


def _resolve_mode(mode: str | None) -> str:
    if mode not in {"cv", "cl"}:
        raise click.ClickException("Use exactly one mode: --cv or --cl")
    return mode


def _ask_for_missing(field_name: str, label: str, data: dict, default: str = "") -> str:
    value = data.get(field_name)
    if value not in (None, ""):
        return value
    return click.prompt(
        click.style(label, fg="white", bold=True),
        default=default,
        show_default=bool(default),
    )


def _collect_compile_data(mode: str, seed_data: dict | None = None) -> dict:
    seed_data = seed_data or {}

    click.echo(click.style("In case of missing fields, please, fill these in: ", fg=COMMAND_COLORS["compile"]))
    click.echo()

    resolved = {}
    resolved["career"] = _ask_for_missing("career", "1) Career", seed_data)
    resolved["job_position"] = _ask_for_missing("job_position", "2) Job Position", seed_data)
    resolved["company_name"] = _ask_for_missing("company_name", "3) Company Name", seed_data)
    resolved["location"] = _ask_for_missing("location", "4) Job Location", seed_data)
    resolved["job_link"] = _ask_for_missing("job_link", "5) Job Link", seed_data, default="")

    if mode == "cl":
        resolved["your_background"] = _ask_for_missing(
            "your_background",
            "Your tailored background",
            seed_data,
        )
        resolved["sentence_first_paragraph"] = _ask_for_missing(
            "sentence_first_paragraph",
            "The company's challenge(s)",
            seed_data,
        )

    return resolved


def compile_with_data(
    *,
    mode: str,
    username: str,
    verbose: bool,
    seed_data: dict | None = None,
):
    replacements = _collect_compile_data(mode, seed_data)
    replacements = build_replacements(mode, replacements)
    template, path = render_and_compile(
        mode=mode,
        username=username,
        replacements=replacements,
        verbose=verbose,
    )
    return replacements, template, path
