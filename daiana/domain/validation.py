"""Validators for LLM JSON outputs."""
from __future__ import annotations

from daiana.utils.constants import REQUIRED_JOB_FIELDS, REQUIRED_SENTENCE_FIELDS


def validate_job_data(data: dict, url: str) -> dict:
    for field in REQUIRED_JOB_FIELDS:
        if field not in data or data[field] is None:
            data[field] = ""
    if not data["job_link"]:
        data["job_link"] = url
    return data


def validate_sentence_data(data: dict) -> dict:
    for field in REQUIRED_SENTENCE_FIELDS:
        if field not in data or data[field] is None:
            data[field] = ""
    return data


def validate_project_data(data: dict, valid_names: set[str]) -> dict:
    selected = data.get("selected", [])
    selected = list(dict.fromkeys(n for n in selected if n in valid_names))[:3]
    data["selected"] = selected
    reasons = data.get("reasons", {})
    data["reasons"] = {k: reasons.get(k, "") for k in selected}
    return data


def validate_background_data(data: dict, valid_backgrounds: set[str]) -> dict:
    if not isinstance(data, dict):
        raise ValueError("Oracle output must be a dict")
    required = ("background_one", "background_two", "background_three")
    for key in required:
        if key not in data:
            raise ValueError(f"Missing required key: {key}")
        if data[key] not in valid_backgrounds:
            raise ValueError(f"Invalid background for {key}: {data[key]}")
    values = [data["background_one"], data["background_two"], data["background_three"]]
    if len(set(values)) != 3:
        raise ValueError(f"Expected 3 distinct backgrounds, got: {values}")
    return {
        "background_one": data["background_one"],
        "background_two": data["background_two"],
        "background_three": data["background_three"],
    }
