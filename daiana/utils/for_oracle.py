import click
import json
from narwhals import Field
import requests
from bs4 import BeautifulSoup
from pathlib import Path
from typing import Dict

from daiana.utils.constants import COMMAND_COLORS, FIELDNAMES


def unicode_to_utf8(raw: str) -> str:
    """Convert escaped Unicode (\\uXXXX) in a string into real UTF‑8 chars."""
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
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; Daiana/0.1; scouting tool)"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    # Workday / job‑board selector may vary; adjust as needed
    content = soup.find("div", class_="jobDescriptionContent")  # or similar
    if content is None:
        content = soup.find("div", {"class": "description-text"})  # fallback

    if content:
        text = content.get_text(strip=True, separator=" ")
    else:
        text = ""

    # Clipping to avoid insane tokens
    return text[:10_000]


def edit_oracle_dict(job: dict) -> dict:
    """
    Ask user to confirm or edit each field in the job dict.
    """
    click.echo()
    click.secho("Please review and edit each field (just press Enter to keep current value).\n",
                fg=COMMAND_COLORS['update'])

    for key in FIELDNAMES:
        current = job.get(key, "") or ""
        new = click.prompt(f"  {key:14}", default=current, type=str)
        if new.strip():
            job[key] = new.strip()
    return job
