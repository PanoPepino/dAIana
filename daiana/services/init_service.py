"""Init / setup service — replaces core/initer.py."""
from pathlib import Path
import os
import shutil

import typer
from dotenv import set_key as dotenv_set_key
from rich.console import Console

from daiana.utils.constants import SUPPORTED_MODELS

console = Console()


def get_local_job_hunt() -> Path:
    source_dir = Path.cwd() / "job_hunt"
    if not source_dir.exists():
        raise typer.BadParameter("Expected a 'job_hunt' folder in the current directory.")
    return source_dir


def ensure_env_file(env_path: Path) -> None:
    env_path.parent.mkdir(parents=True, exist_ok=True)
    env_path.touch(exist_ok=True)


def copy_directory_func() -> None:
    console.print("\n[bold magenta]✦ Copying project directory[/bold magenta]\n")
    source_dir = get_local_job_hunt()
    destination = Path(
        typer.prompt("Where should I copy the [job_hunt] folder?", default=str(Path.home()))
    ).expanduser().resolve()
    destination.mkdir(parents=True, exist_ok=True)
    target_dir = destination / "job_hunt"
    if target_dir.exists():
        if not typer.confirm(f"{target_dir} already exists. Overwrite?", default=False):
            console.print("[yellow]Copy cancelled.[/yellow]")
            raise typer.Exit()
        shutil.rmtree(target_dir)
    shutil.copytree(source_dir, target_dir)
    console.print(f"[bold green]✓ Copied[/bold green] to [cyan]{target_dir}[/cyan]")
    console.print(f"\n[yellow]Next:[/yellow]\n[bold cyan]cd {target_dir}[/bold cyan]\n[bold cyan]daiana init --set_env[/bold cyan]\n")


def _get_provider_defaults(provider: str) -> dict[str, str]:
    defaults = {
        "perplexity": {"model": "sonar", "base_url": "https://api.perplexity.ai", "api_key_name": "PERPLEXITY_API_KEY"},
        "openai": {"model": "gpt-4o-mini", "base_url": "https://api.openai.com/v1", "api_key_name": "OPENAI_API_KEY"},
    }
    return defaults[provider]


def set_env_func() -> None:
    console.print("\n[bold magenta]✦ Setting environment[/bold magenta]\n")
    project_dir = Path.cwd().resolve()
    env_path = project_dir / ".env"
    ensure_env_file(env_path)

    provider = typer.prompt("Which provider are you using?", default="perplexity").strip().lower()
    if provider not in SUPPORTED_MODELS:
        raise typer.BadParameter(f"Unsupported provider. Choose one of: {', '.join(sorted(SUPPORTED_MODELS))}")

    d = _get_provider_defaults(provider)
    model = typer.prompt("Which model?", default=d["model"]).strip()
    if model not in SUPPORTED_MODELS[provider]:
        raise typer.BadParameter(f"Model not supported. Choose one of: {', '.join(sorted(SUPPORTED_MODELS[provider]))}")

    base_url = typer.prompt("Base URL?", default=d["base_url"]).strip()
    api_key_name = typer.prompt("API key env var name?", default=d["api_key_name"]).strip()
    api_key_value = typer.prompt(f"Paste value for {api_key_name}", hide_input=True, confirmation_prompt=True).strip()

    for k, v in [
        ("DAIANA_JOB_HUNT_DIR", str(project_dir)),
        ("DAIANA_PROVIDER", provider),
        ("DAIANA_MODEL", model),
        ("DAIANA_BASE_URL", base_url),
        ("DAIANA_API_KEY_NAME", api_key_name),
        (api_key_name, api_key_value),
    ]:
        dotenv_set_key(str(env_path), k, v)
        os.environ[k] = v

    console.print(f"[bold green]✓ Saved[/bold green] to [cyan]{env_path}[/cyan]")
    console.print(f"[bold green]✓ Provider:[/bold green] [cyan]{provider}[/cyan] / [bold green]Model:[/bold green] [cyan]{model}[/cyan]\n")
    console.print("[yellow]Run daiana commands from inside this folder.[/yellow]\n")
