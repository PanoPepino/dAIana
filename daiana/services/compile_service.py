"""Compile service — replaces core/compiler.py."""
from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

from rich.console import Console

from daiana.infra.csv_repository import rewrite_filename
from daiana.infra.latex_repository import (
    ask_for_missing,
    build_texinputs,
    check_pdflatex,
    detect_project_root,
    extract_errors,
    get_mode_config,
    read_log,
)
from daiana.utils.design.ui import COMMAND_COLORS, rgb

console = Console()
COMPILE = COMMAND_COLORS["compile"]

# Default full-inventory skills block used when oracle --select_skills was not run.
_DEFAULT_SKILLS_BLOCK = (
    "\\cvitem{Backend \\& Architecture}{Python (FastAPI, Django, Flask), "
    "Distributed Systems (gRPC, RabbitMQ, Kafka), Cloud Native (AWS Lambda, Docker, Kubernetes), "
    "Microservices design, System Scalability, Event-driven architecture.}\n"
    "\\cvitem{Data Engineering \\& ML}{SQL (PostgreSQL, Redshift), NoSQL (Redis, MongoDB), "
    "Big Data (Apache Spark, Airflow), ETL pipeline design, MLOps (MLflow, Kubeflow), "
    "Model deployment, Feature stores.}\n"
    "\\cvitem{DevOps \\& Infrastructure}{Infrastructure as Code (Terraform, Pulumi), "
    "CI/CD (GitHub Actions, GitLab CI), Monitoring \\& Observability (Prometheus, Grafana, ELK Stack), "
    "Linux Kernel tuning, Network security.}\n"
    "\\cvitem{Languages \\& Tools}{Python, Rust, Go, TypeScript, C++, Bash, SQL, \\LaTeX{}, "
    "VS Code, IntelliJ, Agile/Scrum.}"
)


def _collect_compile_data(mode: str, seed_data: dict | None = None) -> dict:
    seed_data = seed_data or {}
    console.print(f"[{rgb(COMPILE)}]In case of missing fields, please fill these in:[/{rgb(COMPILE)}]")
    console.print()
    resolved = {
        "career": ask_for_missing("career", "1) Career", seed_data),
        "job_position": ask_for_missing("job_position", "2) Job Position", seed_data),
        "company_name": ask_for_missing("company_name", "3) Company Name", seed_data),
        "location": ask_for_missing("location", "4) Job Location", seed_data, default=""),
        "job_link": ask_for_missing("job_link", "5) Job Link", seed_data, default=""),
    }
    if mode == "cl":
        resolved["your_background"] = ask_for_missing("your_background", "6) Your tailored background", seed_data)
        resolved["sentence_first_paragraph"] = ask_for_missing("sentence_first_paragraph", "7) Company challenge(s)", seed_data)
        resolved["project_one"] = ask_for_missing("project_one", "8) First relevant project", seed_data)
        resolved["project_two"] = ask_for_missing("project_two", "9) Second relevant project", seed_data)
    if mode == "cv":
        resolved["project_one"] = ask_for_missing("project_one", "6) First relevant project", seed_data)
        resolved["project_two"] = ask_for_missing("project_two", "7) Second relevant project", seed_data)
        resolved["project_three"] = ask_for_missing("project_three", "8) Last relevant project", seed_data)
        # Skills block: taken silently from seed_data (set by oracle --select_skills).
        # Not prompted interactively — the rendered LaTeX is not human-typeable.
        resolved["selected_skills_latex"] = seed_data.get("selected_skills_latex", "")
    return resolved


def build_replacements(mode: str, data: dict) -> dict:
    r = {
        "career": data.get("career", ""),
        "job_position": data.get("job_position", ""),
        "company_name": data.get("company_name", ""),
        "location": data.get("location", ""),
        "job_link": data.get("job_link", ""),
    }
    if mode == "cl":
        r.update({
            "your_background": data.get("your_background", ""),
            "sentence_first_paragraph": data.get("sentence_first_paragraph", ""),
            "cp_latex": f"\\body{r['career']}" if r["career"] else "",
            "project_one": f"\\{data.get('project_one', '')}",
            "project_two": f"\\{data.get('project_two', '')}",
        })
    if mode == "cv":
        r.update({
            "project_one": f"\\{data.get('project_one', '')}",
            "project_two": f"\\{data.get('project_two', '')}",
            "project_three": f"\\{data.get('project_three', '')}",
            # Use oracle selection when available, otherwise fall back to full inventory.
            "selected_skills_latex": data.get("selected_skills_latex") or _DEFAULT_SKILLS_BLOCK,
        })
    return r


def render_template(template_path: Path, replacements: dict[str, str], stem_replacement: str = None) -> Path:
    directory_obj, obj_to_copy = template_path.parent, template_path.stem
    slug = rewrite_filename(replacements["company_name"].lower())
    fake = f"{stem_replacement}_{slug}" if stem_replacement else f"{obj_to_copy}_{slug}"
    new_path = Path(f"{directory_obj}/{fake}.tex")
    shutil.copy2(template_path, new_path)
    text = new_path.read_text(encoding="utf-8")
    for placeholder, value in replacements.items():
        text = text.replace(placeholder, value)
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
        relative_output_dir = Path("../pdf_output")
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
        log_path = tmp_tex.parent / f"{stem}.log"
        env = os.environ.copy()
        env["TEXINPUTS"] = texinputs if texinputs else build_texinputs(tmp_root)
        cmd = ["pdflatex", "-interaction=batchmode", "-halt-on-error", str(tmp_tex)]

        for i in range(passes):
            result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                    cwd=tmp_tex.parent, env=env) if silent else \
                     subprocess.run(cmd, capture_output=False, cwd=tmp_tex.parent, env=env)
            if verbose:
                console.print(f"[bold {rgb(COMPILE)}]Pass {i+1}/{passes}:[/bold {rgb(COMPILE)}]")
                console.print(extract_errors(read_log(log_path))[-500:])

        tmp_pdf = tmp_tex.parent / f"{stem}.pdf"
        if not tmp_pdf.exists():
            raise RuntimeError("No PDF produced.")
        shutil.move(tmp_pdf, pdf_path)
        if clean:
            for ext in [".aux", ".log", ".fls", ".fdb_latexmk", ".synctex.gz", ".out", ".tex"]:
                f = tmp_tex.parent / f"{stem}{ext}"
                if f.exists():
                    f.unlink()
            if tex_path.exists():
                tex_path.unlink()

    return pdf_path


def render_and_compile(mode: str, username: str, replacements: dict, verbose: bool = False):
    config = get_mode_config(mode)
    tex = render_template(config["template"], replacements, stem_replacement=f"{username}_{config['addon_name']}")
    path = compile_tex(tex, verbose=verbose)
    return config["template"], path


def compile_with_data(*, mode: str, username: str, verbose: bool, seed_data: dict | None = None):
    replacements = _collect_compile_data(mode, seed_data)
    replacements = build_replacements(mode, replacements)
    template, path = render_and_compile(mode=mode, username=username, replacements=replacements, verbose=verbose)
    return replacements, template, path
