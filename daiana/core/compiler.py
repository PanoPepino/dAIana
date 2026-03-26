import click
import subprocess
import shutil
import os
import tempfile
from typing import Optional
from pathlib import Path
from daiana.utils.for_latex import *


def check_pdflatex() -> bool:
    return shutil.which("pdflatex") is not None


def detect_project_root(tex_file: Path) -> Path:
    for candidate in [tex_file.parent, *tex_file.parent.parents]:
        if (candidate / "cls").exists() or (candidate / "loader").exists():
            return candidate
    return tex_file.parent


def build_texinputs(tmp_root: Path) -> str:
    """
    EXACT bash: ./cls//:./loader//:${TEXINPUTS:-}. Given the structure of the preamble and cls files, this is necessary to import everytime. 

    Note ..

    Observe that the path requires to be changed if the folder arrangement changes. If you are compiling things in a folder at the same level as cls/ and loader/, you will need to adjust this path.
    """

    prefix = f"./:{tmp_root / 'cls'}//./:{tmp_root / 'loader'}//:"
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

    The infamous compiler. To be documented.

    Raises:
        click.ClickException: _description_
        click.ClickException: _description_
        click.ClickException: _description_

    Returns:
        _type_: _description_
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
    else:
        pass
    pdf_path = root/relative_output_dir/f"{stem}.pdf"

    with tempfile.TemporaryDirectory(prefix="daiana-") as tmp_str:
        tmp_root = Path(tmp_str)

        # Mirror project structure
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

        # ✅ 2 PASSES for moderncv
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
                click.echo(f"📋 Pass {i+1}/{passes}:", err=True)
                click.echo(extract_errors(log_text)[-500:], err=True)
            elif not silent and result.returncode != 0:
                log_text = read_log(log_path)
                click.secho(f"⚠ Pass {i+1}/{passes} failed", fg="red", err=True)
                click.echo(extract_errors(log_text), err=True)
            elif not silent:
                click.echo(f"✓ Pass {i+1}/{passes}")

        tmp_pdf = tmp_tex_dir / f"{stem}.pdf"
        if not tmp_pdf.exists():
            if verbose:
                log_text = read_log(log_path)
                click.echo(f"\n❌ No PDF. Log:\n{log_text}")
            raise click.ClickException("No PDF produced.")

        shutil.move(tmp_pdf, pdf_path)

        if clean:
            for ext in [".aux", ".log", ".fls", ".fdb_latexmk", ".synctex.gz", ".out", ".tex"]:
                f = tmp_tex_dir / f"{stem}{ext}"
                if f.exists():
                    f.unlink()
            tex_path.unlink()  # To clean the copied .tex file

        open_pdf(pdf_path)

    if not silent:
        click.echo(f"✓ {pdf_path}")
    return pdf_path
