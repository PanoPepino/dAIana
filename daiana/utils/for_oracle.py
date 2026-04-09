import click
import requests
import re
import json
import os

from bs4 import BeautifulSoup
from openai import OpenAI
from dotenv import load_dotenv

from daiana.utils.constants import (
    COMMAND_COLORS,
    NOISE_PATTERNS,
)
from daiana.utils.constants import (
    REQUIRED_JOB_FIELDS, VALID_CAREERS,
    REQUIRED_SENTENCE_FIELDS
)

from daiana.utils.prompts import BACKGROUND, PROJECT_NAME_TO_LATEX


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


def edit_oracle_dict(job: dict) -> dict:
    """Ask user to confirm or edit each field in the job dict."""
    click.echo()
    click.secho(
        "Please review and edit each field (just press Enter to keep current value).\n",
        fg=COMMAND_COLORS["update"],
    )
    for key in job.keys():
        current = job.get(key, "") or ""
        new = click.prompt(f"  {key:14}", default=current, type=str)
        if new.strip():
            job[key] = new.strip()
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

    # Safe extraction with empty string defaults
    normalized = {
        "project_one": selection.get("selected_1", ""),
        "project_two": selection.get("selected_2", ""),
        "project_three": selection.get("selected_3", ""),
        "reason_name_1": selection.get("reason_name_1", ""),
        "reason_name_2": selection.get("reason_name_2", ""),
        "reason_name_3": selection.get("reason_name_3", ""),
    }

    # Validation: warn if reasons are missing
    missing_reasons = [k for k, v in normalized.items()
                       if k.startswith("reason_name_") and not v.strip()]
    if missing_reasons:
        click.secho(f"WARNING: Missing reasons for {len(missing_reasons)} projects", fg="yellow")

    return normalized


# ── Validators ────────────────────────────────────────────────────────────────

def _validate_job_data(data: dict, url: str) -> dict:
    for field in REQUIRED_JOB_FIELDS:
        if field not in data or data[field] is None:
            data[field] = ""
    if not data["job_link"]:
        data["job_link"] = url
    if data["career"] not in VALID_CAREERS:
        data["career"] = "rd"
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

def build_perplexity_client() -> OpenAI:
    load_dotenv()
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        raise ValueError("PERPLEXITY_API_KEY not found in environment or .env")
    return OpenAI(api_key=api_key, base_url="https://api.perplexity.ai")
