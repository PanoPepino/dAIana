"""Init / setup service — replaces core/initer.py."""
from operator import ne
from pathlib import Path
import os
import shutil

import typer
from dotenv import set_key as dotenv_set_key
from rich.console import Console

from daiana.utils.constants import SUPPORTED_MODELS
from daiana.utils.design.colors import COMMAND_COLORS, NEUTRAL
from daiana.utils.design.ui import rgb, _panel


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
    init_color = rgb(COMMAND_COLORS["init"])
    neutral_color = rgb(NEUTRAL)

    console.print(f"\n[bold {init_color}]Copying[/bold {init_color}] [white]project directory[/white]\n")

    source_dir = get_local_job_hunt()

    console.print(
        f"[bold {init_color}]Where should I copy the [job_hunt] directory?[/bold {init_color}]"
    )
    destination = Path(
        typer.prompt("", default=str(Path.home()))
    ).expanduser().resolve()

    destination.mkdir(parents=True, exist_ok=True)
    target_dir = destination / "job_hunt"

    if target_dir.exists():
        console.print("")
        console.print(
            f"[{neutral_color}]{target_dir} already exists.[/{neutral_color}] "
            f"[bold {init_color}]Overwrite[/bold {init_color}]?"
        )
        if not typer.confirm("", default=False):
            console.print(f"[{neutral_color}]Copy cancelled.[/{neutral_color}]")
            raise typer.Exit()
        shutil.rmtree(target_dir)

    shutil.copytree(source_dir, target_dir)
    console.print("")
    console.print(
        _panel(
            "Directory copied",
            [
                ("Source:", str(source_dir)),
                ("Target:", str(target_dir)),
            ],
            color=COMMAND_COLORS["init"],
        )
    )
    console.print()
    console.print(
        f"[{init_color}]Next steps:[/{init_color}]\n"
        f"\n"
        f"[bold cyan]cd {target_dir}[/bold cyan]\n"
        f"[bold {init_color}]daiana init --set_env[/bold {init_color}]\n"
    )


def _get_provider_defaults(provider: str) -> dict[str, str]:
    defaults = {
        "perplexity": {"model": "sonar", "base_url": "https://api.perplexity.ai", "api_key_name": "PERPLEXITY_API_KEY"},
        "openai": {"model": "gpt-4o-mini", "base_url": "https://api.openai.com/v1", "api_key_name": "OPENAI_API_KEY"},
    }
    return defaults[provider]


def _prompt_choice(question: str, choices: list[str], default: str) -> str:
    init_color = rgb(COMMAND_COLORS["init"])
    neutral_color = rgb(NEUTRAL)

    while True:
        console.print(
            f"[bold {init_color}]{question}[/bold {init_color}] "
            f"[{neutral_color}]({', '.join(choices)})[/{neutral_color}]",
            end=" ",
        )
        answer = typer.prompt("", prompt_suffix="").strip()

        if not answer:
            answer = default

        if answer in choices:
            return answer

        console.print(
            f"[bold red]Invalid choice.[/bold red] "
            f"[{neutral_color}]Please choose one of: {', '.join(choices)}[/{neutral_color}]"
        )


def set_env_func() -> None:
    init_color = rgb(COMMAND_COLORS["init"])
    neutral_color = rgb(NEUTRAL)

    console.print(f"\n[bold {init_color}]Setting environment[/bold {init_color}]\n")

    project_dir = Path.cwd().resolve()
    env_path = project_dir / ".env"
    ensure_env_file(env_path)

    provider_choices = sorted(SUPPORTED_MODELS.keys())
    provider = _prompt_choice(
        question="Which provider are you using?",
        choices=provider_choices,
        default="perplexity",
    )

    provider_defaults = _get_provider_defaults(provider)

    model_choices = sorted(SUPPORTED_MODELS[provider])
    model = _prompt_choice(
        question="Which model do you want to use?",
        choices=model_choices,
        default=provider_defaults["model"],
    )

    base_url_choices = [provider_defaults["base_url"]]
    base_url = _prompt_choice(
        question="Which base URL should be used?",
        choices=base_url_choices,
        default=provider_defaults["base_url"],
    )

    api_key_name_choices = [provider_defaults["api_key_name"]]
    api_key_name = _prompt_choice(
        question="Which API key env var name should be used?",
        choices=api_key_name_choices,
        default=provider_defaults["api_key_name"],
    )

    console.print(
        f"[bold {init_color}]Paste the value for {api_key_name}:[/bold {init_color}] ",
        end=""
    )
    api_key_value = typer.prompt(
        "",
        prompt_suffix="",
        hide_input=True,
        confirmation_prompt=True,
    ).strip()

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

    console.print()
    console.print(
        _panel(
            "Environment saved",
            [
                ("Project dir:", str(project_dir)),
                ("Env file:", str(env_path)),
                ("Provider:", provider),
                ("Model:", model),
                ("Base URL:", base_url),
                ("API key env:", api_key_name),
            ],
            color=COMMAND_COLORS["init"],
        )
    )
    console.print()
