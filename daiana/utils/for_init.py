from pathlib import Path
import os
import random

import typer
from dotenv import load_dotenv
from openai import OpenAI
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


def _mask_secret(value: str) -> str:
    if not value:
        return ""
    if len(value) <= 8:
        return "*" * len(value)
    return f"{value[:4]}...{value[-4:]}"


def _resolve_job_hunt_dir() -> Path:
    env_dir = os.getenv("DAIANA_JOB_HUNT_DIR")
    if env_dir:
        path = Path(env_dir).expanduser().resolve()
        if path.exists():
            return path

    cwd = Path.cwd().resolve()
    if (cwd / "prompts").exists():
        return cwd

    raise typer.BadParameter(
        "Missing job_hunt directory. Run this inside a job_hunt folder or set DAIANA_JOB_HUNT_DIR."
    )


def _load_job_hunt_env() -> Path:
    job_hunt_path = _resolve_job_hunt_dir()
    env_path = job_hunt_path / ".env"

    if not env_path.exists():
        raise typer.BadParameter(
            f".env not found in {job_hunt_path}. Run 'daiana init --set_env' first."
        )

    load_dotenv(dotenv_path=env_path, override=False)
    os.environ["DAIANA_JOB_HUNT_DIR"] = str(job_hunt_path)
    return env_path


def get_provider() -> str:
    _load_job_hunt_env()
    provider = os.getenv("DAIANA_PROVIDER", "perplexity").strip().lower()

    if provider not in SUPPORTED_MODELS:
        valid = ", ".join(sorted(SUPPORTED_MODELS))
        raise typer.BadParameter(
            f"Unsupported provider '{provider}'. Supported providers: {valid}"
        )

    return provider


def get_default_model() -> str:
    _load_job_hunt_env()
    provider = get_provider()
    model = os.getenv("DAIANA_MODEL")

    defaults = {
        "perplexity": "sonar",
        "openai": "gpt-4o-mini",
    }

    if not model:
        return defaults[provider]

    model = model.strip()
    if model not in SUPPORTED_MODELS[provider]:
        valid = ", ".join(sorted(SUPPORTED_MODELS[provider]))
        raise typer.BadParameter(
            f"Model '{model}' is not supported for provider '{provider}'. Choose one of: {valid}"
        )

    return model


def build_llm_client() -> OpenAI:
    env_path = _load_job_hunt_env()

    api_key_name = os.getenv("DAIANA_API_KEY_NAME", "USER_API_KEY")
    api_key = os.getenv(api_key_name)
    if not api_key:
        raise typer.BadParameter(f"{api_key_name} not found in {env_path}")

    provider = get_provider()
    default_base_urls = {
        "perplexity": "https://api.perplexity.ai",
        "openai": "https://api.openai.com/v1",
    }
    base_url = os.getenv("DAIANA_BASE_URL", default_base_urls[provider])

    return OpenAI(
        api_key=api_key,
        base_url=base_url,
    )


def inspect_loaded_environment() -> dict:
    env_path = _load_job_hunt_env()
    provider = get_provider()
    model = get_default_model()

    api_key_name = os.getenv("DAIANA_API_KEY_NAME", "USER_API_KEY")
    api_key_value = os.getenv(api_key_name, "")
    base_url = os.getenv(
        "DAIANA_BASE_URL",
        "https://api.perplexity.ai" if provider == "perplexity" else "https://api.openai.com/v1",
    )
    job_hunt_dir = os.getenv("DAIANA_JOB_HUNT_DIR", "")

    return {
        "job_hunt_dir": job_hunt_dir,
        "env_path": str(env_path),
        "provider": provider,
        "base_url": base_url,
        "model": model,
        "api_key_name": api_key_name,
        "api_key_masked": _mask_secret(api_key_value),
    }


def test_loaded_environment() -> dict:
    info = inspect_loaded_environment()

    try:
        client = build_llm_client()
        countries = ["Japan", "Brazil", "Canada", "Kenya", "Portugal", "Chile", "India", "Morocco"]
        country = random.choice(countries)

        response = client.chat.completions.create(
            model=info["model"],
            messages=[
                {"role": "system", "content": "You are a concise factual assistant."},
                {
                    "role": "user",
                    "content": f"Give exactly one short factual sentence about {country}. No bullet points. No markdown. Under 20 words.",
                },
            ],
            temperature=0.0,
            stream=False,
        )

        info["test_status"] = "success"
        info["test_country"] = country
        info["test_fact"] = response.choices[0].message.content.strip()
        info["test_error"] = ""
    except Exception as exc:
        info["test_status"] = "failed"
        info["test_country"] = ""
        info["test_fact"] = ""
        info["test_error"] = str(exc)

    return info


def check_api_environment() -> None:
    info = test_loaded_environment()

    console.print("\n[bold magenta]✦ Environment check[/bold magenta]\n")
    for key, value in info.items():
        console.print(f"[bold]{key}:[/bold] {value}")
    console.print()
