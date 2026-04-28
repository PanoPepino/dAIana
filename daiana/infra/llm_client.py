"""Build the OpenAI-compatible LLM client from Settings."""
from __future__ import annotations

from openai import OpenAI

from daiana.config.settings import Settings, load_settings
import click


def build_client(settings: Settings | None = None) -> OpenAI:
    """Build and return an OpenAI-compatible client."""
    s = settings or load_settings()
    if not s.api_key_value:
        raise click.ClickException(
            f"{s.api_key_name} not found in {s.env_path}"
        )
    return OpenAI(api_key=s.api_key_value, base_url=s.base_url)
