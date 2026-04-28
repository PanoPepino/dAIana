"""Job posting HTML scraper."""
from __future__ import annotations

import re

import requests
from bs4 import BeautifulSoup

from daiana.utils.constants import SCRAPE_SELECTORS, NOISE_PATTERNS, SCRAPE_CHAR_LIMIT


def scrape_job_text(url: str) -> str:
    """Download a job posting URL and return cleaned plain text."""
    headers = {"User-Agent": "Mozilla/5.0 (compatible; Daiana/0.1; scouting tool)"}
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    for selector in SCRAPE_SELECTORS:
        content = soup.find("div", selector)
        if content:
            return _clean_text(content.get_text(strip=True, separator=" "))

    for tag in soup(["script", "style", "nav", "header", "footer"]):
        tag.decompose()
    return _clean_text(soup.get_text(strip=True, separator=" "))


def _clean_text(text: str) -> str:
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    lines = [ln for ln in lines if not NOISE_PATTERNS.search(ln)]
    cleaned = re.sub(r"\s{2,}", " ", " ".join(lines))
    return cleaned[:SCRAPE_CHAR_LIMIT]
