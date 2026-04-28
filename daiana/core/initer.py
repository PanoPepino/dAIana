from pathlib import Path
import os
import shutil

import typer
from dotenv import set_key as dotenv_set_key
from rich.console import Console


from daiana.utils.for_init import ensure_env_file, get_local_job_hunt
from daiana.utils.constants import SUPPORTED_MODELS

console = Console()


def copy_directory_func() -> None:
    console.print("\n[bold magenta]✦ Copying project directory[/bold magenta]\n")

    source_dir = get_local_job_hunt()
    destination = Path(
        typer.prompt(
            "Where should I copy the [job_hunt] folder?",
            default=str(Path.home()),
        )
    ).expanduser().resolve()

    destination.mkdir(parents=True, exist_ok=True)
    target_dir = destination / "job_hunt"

    if target_dir.exists():
        overwrite = typer.confirm(f"{target_dir} already exists. Overwrite?", default=False)
        if not overwrite:
            console.print("[yellow]Copy cancelled.[/yellow]")
            raise typer.Exit()
        shutil.rmtree(target_dir)

    shutil.copytree(source_dir, target_dir)

    console.print(f"[bold green]✓ Copied[/bold green] to [cyan]{target_dir}[/cyan]")
    console.print("\n[yellow]Next:[/yellow]")
    console.print(f"[bold cyan]cd {target_dir}[/bold cyan]")
    console.print("[bold cyan]daiana init --set_env[/bold cyan]\n")


def _get_provider_defaults(provider: str) -> dict[str, str]:
    defaults = {
        "perplexity": {
            "model": "sonar",
            "base_url": "https://api.perplexity.ai",
            "api_key_name": "PERPLEXITY_API_KEY",
        },
        "openai": {
            "model": "gpt-4o-mini",
            "base_url": "https://api.openai.com/v1",
            "api_key_name": "OPENAI_API_KEY",
        },
    }
    return defaults[provider]


def set_env_func() -> None:
    console.print("\n[bold magenta]✦ Setting environment[/bold magenta]\n")

    project_dir = Path.cwd().resolve()
    env_path = project_dir / ".env"
    ensure_env_file(env_path)

    provider = typer.prompt(
        "Which provider are you using?",
        default="perplexity",
    ).strip().lower()

    if provider not in SUPPORTED_MODELS:
        valid = ", ".join(sorted(SUPPORTED_MODELS))
        raise typer.BadParameter(f"Unsupported provider '{provider}'. Choose one of: {valid}")

    defaults = _get_provider_defaults(provider)

    model = typer.prompt(
        "Which model should dAIana use?",
        default=defaults["model"],
    ).strip()

    if model not in SUPPORTED_MODELS[provider]:
        valid = ", ".join(sorted(SUPPORTED_MODELS[provider]))
        raise typer.BadParameter(
            f"Model '{model}' is not supported for provider '{provider}'. Choose one of: {valid}"
        )

    base_url = typer.prompt(
        "Which base URL should dAIana use?",
        default=defaults["base_url"],
    ).strip()

    api_key_name = typer.prompt(
        "Which environment variable name should store the API key?",
        default=defaults["api_key_name"],
    ).strip()

    api_key_value = typer.prompt(
        f"Paste the value for {api_key_name}",
        hide_input=True,
        confirmation_prompt=True,
    ).strip()

    dotenv_set_key(str(env_path), "DAIANA_JOB_HUNT_DIR", str(project_dir))
    dotenv_set_key(str(env_path), "DAIANA_PROVIDER", provider)
    dotenv_set_key(str(env_path), "DAIANA_MODEL", model)
    dotenv_set_key(str(env_path), "DAIANA_BASE_URL", base_url)
    dotenv_set_key(str(env_path), "DAIANA_API_KEY_NAME", api_key_name)
    dotenv_set_key(str(env_path), api_key_name, api_key_value)

    os.environ["DAIANA_JOB_HUNT_DIR"] = str(project_dir)
    os.environ["DAIANA_PROVIDER"] = provider
    os.environ["DAIANA_MODEL"] = model
    os.environ["DAIANA_BASE_URL"] = base_url
    os.environ["DAIANA_API_KEY_NAME"] = api_key_name
    os.environ[api_key_name] = api_key_value

    console.print(f"[bold green]✓ Saved[/bold green] environment in [cyan]{env_path}[/cyan]")
    console.print(f"[bold green]✓ Provider:[/bold green] [cyan]{provider}[/cyan]")
    console.print(f"[bold green]✓ Model:[/bold green] [cyan]{model}[/cyan]")
    console.print(f"[bold green]✓ Base URL:[/bold green] [cyan]{base_url}[/cyan]")
    console.print(f"[bold green]✓ API key name:[/bold green] [cyan]{api_key_name}[/cyan]")
    console.print("[bold green]✓ API key stored[/bold green]\n")
    console.print("[yellow]From now on, just run daiana commands inside this folder.[/yellow]\n")
