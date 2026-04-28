from __future__ import annotations
from pathlib import Path
from daiana.utils.design.ui import COMMAND_COLORS, rgb
from rich.prompt import Prompt
from rich.console import Console
import requests
import re
import json
import os

from bs4 import BeautifulSoup
from openai import OpenAI
from dotenv import load_dotenv
from daiana.utils.constants import SUPPORTED_MODELS
import typer

from daiana.utils.constants import (
    NOISE_PATTERNS,
    REQUIRED_JOB_FIELDS,
    REQUIRED_SENTENCE_FIELDS
)

from daiana.utils.prompts import BACKGROUND, PROJECT_NAME_TO_LATEX

from daiana.utils.design.styles import COMMAND_COLORS


def unicode_to_utf8(raw: str) -> str:
    """Convert escaped Unicode (\\uXXXX) in a string into real UTF-8 chars."""
    try:
        decoded = raw.encode("latin1").decode("unicode_escape")
        return decoded.encode("latin1").decode("utf-8")
    except Exception:
        return raw


def clean_city_location(loc: str) -> str:
    """Extract only the city from the location string."""
    if not loc.strip():
        return "Unknown"
    parts = [p.strip() for p in loc.split(",") if p.strip()]
    if parts:
        return parts[-1]
    return "Unknown"


def scrape_job_text(url: str) -> str:
    headers = {"User-Agent": "Mozilla/5.0 (compatible; Daiana/0.1; scouting tool)"}
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # Try known job board selectors first
    for selector in [
        {"class": "jobDescriptionContent"},
        {"class": "description-text"},
        {"class": "job-description"},
        {"id": "job-description"},
        {"class": "posting-description"},
    ]:
        content = soup.find("div", selector)
        if content:
            return content.get_text(strip=True, separator=" ")[:10_000]

    # Nuclear fallback — strip all tags, take body text
    for tag in soup(["script", "style", "nav", "header", "footer"]):
        tag.decompose()
    return soup.get_text(strip=True, separator=" ")[:10_000]


def _clean_text(text: str) -> str:
    """Collapse whitespace, strip noise lines, cap at 10k chars."""
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    lines = [ln for ln in lines if not NOISE_PATTERNS.search(ln)]
    cleaned = " ".join(lines)
    cleaned = re.sub(r"\s{2,}", " ", cleaned)
    return cleaned[:10_000]


console = Console()


def edit_oracle_dict(job: dict) -> dict:
    console.print()
    console.print(
        f"[{rgb(COMMAND_COLORS['update'])}]Please review and edit each field "
        f"(just press Enter to keep current value).[/ {rgb(COMMAND_COLORS['update'])}]"
    )
    console.print()

    for key in job.keys():
        original = job.get(key, "")

        current = str(original or "")
        new_value = Prompt.ask(
            f"[bold white]{key:14}[/bold white]",
            default=current,
            show_default=True,
        ).strip()

        if new_value:
            job[key] = new_value

    for key, value in job.items():
        if not isinstance(value, str):
            raise TypeError(
                f"edit_oracle_dict produced non-string field: {key} -> "
                f"{type(value).__name__}: {repr(value)}"
            )

    return job

# ── JSON helpers ──────────────────────────────────────────────────────────────


def _clean_llm_json(raw: str) -> str:
    if not isinstance(raw, str):
        raise ValueError("Oracle response must be a string before JSON parsing")
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    cleaned = cleaned.replace("\u00a0", " ").strip()
    return cleaned


def parse_oracle_json(raw: str) -> dict:
    cleaned = _clean_llm_json(raw)
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        brace_match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if brace_match:
            try:
                data = json.loads(brace_match.group())
            except json.JSONDecodeError:
                raise ValueError(f"Oracle returned invalid JSON: {exc}\nRaw: {raw}") from exc
        else:
            raise ValueError(f"Oracle returned invalid JSON: {exc}\nRaw: {raw}") from exc
    if not isinstance(data, dict):
        raise ValueError("Oracle JSON must decode into a dictionary")
    return data


def normalize_project_selection(selection: dict) -> dict:
    if not isinstance(selection, dict):
        raise ValueError("Project selection must be a dict")
    normalized = {
        "project_one": selection.get("selected_1", ""),
        "project_two": selection.get("selected_2", ""),
        "project_three": selection.get("selected_3", ""),
        "reason_selected_1": selection.get("reason_selected_1", ""),
        "reason_selected_2": selection.get("reason_selected_2", ""),
        "reason_selected_3": selection.get("reason_selected_3", ""),
    }

    missing_reasons = [
        key
        for key, value in normalized.items()
        if key.startswith("reason_selected_") and not str(value).strip()
    ]

    if missing_reasons:
        console.print()

        console.print(
            f"[yellow]WARNING:[/yellow] Missing reasons for {len(missing_reasons)} projects"
        )
        console.print()

    return normalized

# ── Validators ────────────────────────────────────────────────────────────────


def _validate_job_data(data: dict, url: str) -> dict:
    for field in REQUIRED_JOB_FIELDS:
        if field not in data or data[field] is None:
            data[field] = ""
    if not data["job_link"]:
        data["job_link"] = url
    return data


def _validate_sentence_data(data: dict) -> dict:
    for field in REQUIRED_SENTENCE_FIELDS:
        if field not in data or data[field] is None:
            data[field] = ""
    return data


def _validate_project_data(data: dict) -> dict:
    valid_names = set(PROJECT_NAME_TO_LATEX.keys())
    selected = data.get("selected", [])
    # Keep only valid names, deduplicate, cap at 3
    selected = list(dict.fromkeys(n for n in selected if n in valid_names))[:3]
    data["selected"] = selected
    # Ensure reasons dict exists and only contains selected keys
    reasons = data.get("reasons", {})
    data["reasons"] = {k: reasons.get(k, "") for k in selected}
    return data


def _validate_background_data(data: dict) -> dict:
    required = ("background_one", "background_two", "background_three")
    valid = set(BACKGROUND)

    if not isinstance(data, dict):
        raise ValueError("Oracle output must be a dict")

    for key in required:
        if key not in data:
            raise ValueError(f"Missing required key: {key}")
        if data[key] not in valid:
            raise ValueError(f"Invalid background for {key}: {data[key]}")

    values = [data["background_one"], data["background_two"], data["background_three"]]
    if len(set(values)) != 3:
        raise ValueError(f"Expected 3 distinct backgrounds, got: {values}")

    return {
        "background_one": data["background_one"],
        "background_two": data["background_two"],
        "background_three": data["background_three"],
    }


def dict_values_to_string(d: dict, sep: str = ",") -> str:
    """
    Join all dict values with separator. Works for any dict.
    """

    return sep.join(d.values())


def dict_values_to_sentence(d: dict, sep: str = ", ") -> str:
    """
    Join all dict values into a natural-language string.
    - {"a": "x", "b": "y", "c": "z"} -> "x, y and z"
    """
    values = [str(v) for v in d.values() if v not in (None, "")]

    if not values:
        return ""
    if len(values) == 1:
        return values[0]
    if len(values) == 2:
        return " and ".join(values)

    return f"{sep.join(values[:-1])} and {values[-1]}"


# ── Client ────────────────────────────────────────────────────────────────────


def _load_job_hunt_env() -> Path:
    job_hunt_dir = os.getenv("DAIANA_JOB_HUNT_DIR")
    if not job_hunt_dir:
        raise ValueError("DAIANA_JOB_HUNT_DIR is not set")

    job_hunt_path = Path(job_hunt_dir).expanduser().resolve()
    env_path = job_hunt_path / ".env"

    if not env_path.exists():
        raise ValueError(f".env not found in {job_hunt_path}")

    load_dotenv(dotenv_path=env_path, override=False)
    return env_path


def get_provider() -> str:
    _load_job_hunt_env()
    provider = os.getenv("DAIANA_PROVIDER", "perplexity").strip().lower()

    if provider not in SUPPORTED_MODELS:
        valid = ", ".join(sorted(SUPPORTED_MODELS))
        raise typer.BadParameter(f"Unsupported provider '{provider}'. Supported providers: {valid}")

    return provider


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


def get_default_model() -> str:
    _load_job_hunt_env()
    return os.getenv("DAIANA_MODEL", "sonar-pro")
