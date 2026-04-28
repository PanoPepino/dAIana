"""Single source of truth for all environment, path, provider, and model config."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

import click
from dotenv import load_dotenv

from daiana.utils.constants import SUPPORTED_MODELS


@dataclass
class Settings:
    job_hunt_dir: Path
    env_path: Path
    provider: str
    model: str
    base_url: str
    api_key_name: str
    api_key_value: str


def _resolve_job_hunt_dir() -> Path:
    env_dir = os.getenv("DAIANA_JOB_HUNT_DIR")
    if env_dir:
        path = Path(env_dir).expanduser().resolve()
        if path.exists():
            return path

    cwd = Path.cwd().resolve()
    if (cwd / "prompts").exists():
        return cwd

    raise click.ClickException(
        "Missing job_hunt directory. Run inside a job_hunt folder or set DAIANA_JOB_HUNT_DIR."
    )


def load_settings() -> Settings:
    """Load and validate all runtime settings from env / .env file."""
    job_hunt_dir = _resolve_job_hunt_dir()
    env_path = job_hunt_dir / ".env"

    if not env_path.exists():
        raise click.ClickException(
            f".env not found in {job_hunt_dir}. Run 'daiana init --set_env' first."
        )

    load_dotenv(dotenv_path=env_path, override=False)
    os.environ["DAIANA_JOB_HUNT_DIR"] = str(job_hunt_dir)

    provider = os.getenv("DAIANA_PROVIDER", "perplexity").strip().lower()
    if provider not in SUPPORTED_MODELS:
        valid = ", ".join(sorted(SUPPORTED_MODELS))
        raise click.ClickException(
            f"Unsupported provider '{provider}'. Supported providers: {valid}"
        )

    model_raw = os.getenv("DAIANA_MODEL", "").strip()
    defaults = {"perplexity": "sonar", "openai": "gpt-4o-mini"}
    model = model_raw if model_raw else defaults[provider]
    if model not in SUPPORTED_MODELS[provider]:
        valid = ", ".join(sorted(SUPPORTED_MODELS[provider]))
        raise click.ClickException(
            f"Model '{model}' not supported for '{provider}'. Choose one of: {valid}"
        )

    default_base_urls = {
        "perplexity": "https://api.perplexity.ai",
        "openai": "https://api.openai.com/v1",
    }
    base_url = os.getenv("DAIANA_BASE_URL", default_base_urls[provider]).strip()
    api_key_name = os.getenv("DAIANA_API_KEY_NAME", "USER_API_KEY").strip()
    api_key_value = os.getenv(api_key_name, "").strip()

    return Settings(
        job_hunt_dir=job_hunt_dir,
        env_path=env_path,
        provider=provider,
        model=model,
        base_url=base_url,
        api_key_name=api_key_name,
        api_key_value=api_key_value,
    )


def mask_secret(value: str) -> str:
    if not value:
        return ""
    if len(value) <= 8:
        return "*" * len(value)
    return f"{value[:4]}...{value[-4:]}"
