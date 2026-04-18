from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

from rich.console import Console

from daiana.utils.for_csv import rewrite_filename
from daiana.utils.for_latex import (
    _ask_for_missing,
    build_texinputs,
    check_pdflatex,
    detect_project_root,
    extract_errors,
    get_mode_config,
    read_log,
)
from daiana.utils.ui import COMMAND_COLORS, rgb

console = Console()

COMPILE = COMMAND_COLORS["compile"]


def _collect_compile_data(mode: str, seed_data: dict | None = None) -> dict:
    seed_data = seed_data or {}

    console.print(f"[{rgb(COMPILE)}]In case of missing fields, please, fill these in:[/{rgb(COMPILE)}]")
    console.print()

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
                "project_one": f"\\{data.get('project_one', '')}",
                "project_two": f"\\{data.get('project_two', '')}",
            }
        )

    if mode == "cv":
        replacements.update(
            {
                "project_one": f"\\{data.get('project_one', '')}",
                "project_two": f"\\{data.get('project_two', '')}",
                "project_three": f"\\{data.get('project_three', '')}",
            }
        )

    return replacements


def render_template(
    template_path: Path,
    replacements: dict[str, str],
    stem_replacement: str = None,
) -> Path:
    directory_obj, obj_to_copy = template_path.parent, template_path.stem
    company_pos_ending = rewrite_filename(replacements["company_name"].lower())
    fake_template = f"{stem_replacement}_{company_pos_ending}" if stem_replacement else f"{obj_to_copy}_{company_pos_ending}"
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
    passes: int = 2,
) -> Path:
    if not check_pdflatex():
        raise RuntimeError("pdflatex not found.")

    tex_path = tex_file.absolute()
    if not tex_path.exists():
        raise RuntimeError(f"TeX file not found: {tex_path}")

    stem = tex_path.stem
    root = Path(project_root).absolute() if project_root else detect_project_root(tex_path)
    if relative_output_dir is None:
        relative_output_dir = Path("output")
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

        cmd = ["pdflatex", "-interaction=batchmode", "-halt-on-error", str(tmp_tex)]

        for i in range(passes):
            if silent:
                result = subprocess.run(
                    cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    cwd=tmp_tex_dir,
                    env=env,
                )
            else:
                result = subprocess.run(cmd, capture_output=False, cwd=tmp_tex_dir, env=env)

            if verbose:
                log_text = read_log(log_path)
                console.print(f"[bold {rgb(COMPILE)}]📋 Pass {i + 1}/{passes}:[/bold {rgb(COMPILE)}]")
                console.print(extract_errors(log_text)[-500:])
            elif not silent and result.returncode != 0:
                log_text = read_log(log_path)
                console.print(f"[bold red]⚠ Pass {i + 1}/{passes} failed[/bold red]")
                console.print(extract_errors(log_text))
            elif not silent:
                console.print(f"[green]✓ Pass {i + 1}/{passes}[/green]")

        tmp_pdf = tmp_tex_dir / f"{stem}.pdf"
        if not tmp_pdf.exists():
            if verbose:
                log_text = read_log(log_path)
                console.print()
                console.print(f"[bold red]❌ No PDF. Log:[/bold red]")
                console.print(log_text)
            raise RuntimeError("No PDF produced.")

        shutil.move(tmp_pdf, pdf_path)

        if clean:
            for ext in [".aux", ".log", ".fls", ".fdb_latexmk", ".synctex.gz", ".out", ".tex"]:
                f = tmp_tex_dir / f"{stem}{ext}"
                if f.exists():
                    f.unlink()
            if tex_path.exists():
                tex_path.unlink()

    if not silent:
        console.print(f"[green]✓ {pdf_path}[/green]")
    return pdf_path


def render_and_compile(
    mode: str,
    username: str,
    replacements: dict,
    verbose: bool = False,
):
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
    replacements = _collect_compile_data(mode, seed_data)
    replacements = build_replacements(mode, replacements)
    template, path = render_and_compile(
        mode=mode,
        username=username,
        replacements=replacements,
        verbose=verbose,
    )
    return replacements, template, path
