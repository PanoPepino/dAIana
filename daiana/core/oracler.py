"""
This file contains all the logic to use API requests to the given AI and to display the results in your terminal.
"""

import json
import typer

import os

from rich.console import Console
from typing import Dict
from openai import OpenAI

from daiana.utils.design.colors import COMMAND_COLORS
from daiana.utils.for_init import _mask_secret, _load_job_hunt_env, get_default_model, get_provider
from daiana.utils.constants import NON_EDITABLE
from daiana.utils.design.ui import (
    rgb,
    _display_oracle_result,
    _display_updated_fields,
    _show_active_modes,
)

from daiana.utils.for_oracle import (
    build_llm_client,
    dict_values_to_sentence,
    edit_oracle_dict,
    get_default_model,
    parse_oracle_json,
    unicode_to_utf8,
    scrape_job_text,
    clean_city_location,
    _validate_job_data,
    _validate_project_data,
    _validate_sentence_data,
    _validate_background_data,
    normalize_project_selection,
)

from daiana.utils.prompts import (
    BACKGROUND,
    BACKGROUND_PROMPT,
    JOB_PROMPT,
    SENTENCE_PROMPT,
    PROJECTS_PROMPT,
    SENTENCE_SCHEMA,
    PROJECTS_SCHEMA,
    BACKGROUND_SCHEMA,
    PROJECTS_PAYLOAD,
    PROJECT_NAME_TO_LATEX,
    BACKGROUND_PAYLOAD,
    JOB_SCHEMA,
)


# ── User-content builders ─────────────────────────────────────────────────────

def build_job_user_content(job_text: str) -> str:
    schema_json = json.dumps(JOB_SCHEMA, ensure_ascii=False, separators=(",", ":"))
    career_rule = JOB_SCHEMA.get("career", "")
    return (
        f"Job text:\n{job_text}\n\n"
        f"Return ONLY valid JSON matching this schema:\n{schema_json}\n\n"
        "Rules:\n"
        "1) job_position must be in English.\n"
        "2) location: city only, UTF-8 chars, no postal codes.\n"
        f"3) career MUST be one of: {career_rule}.\n"
        "Do not invent any career.\n"
    )


def build_sentence_user_content(job_text: str, url: str) -> str:
    schema_json = json.dumps(SENTENCE_SCHEMA, ensure_ascii=False, separators=(",", ":"))
    return (
        f"Job URL:\n{url}\n\n"
        f"Job text:\n{job_text}\n\n"
        f"Fill this JSON schema exactly:\n{schema_json}"
    )


def build_project_user_content(job_text: str) -> str:
    schema_json = json.dumps(PROJECTS_SCHEMA, ensure_ascii=False, separators=(",", ":"))
    valid_names = ", ".join(PROJECT_NAME_TO_LATEX.keys())
    return (
        f"Job posting:\n{job_text}\n\n"
        f"Available projects:\n{PROJECTS_PAYLOAD}\n\n"
        f"Valid names: {valid_names}\n\n"
        f"Return ONLY valid JSON matching this schema:\n{schema_json}"
    )


def build_background_user_content(job_text: str) -> str:
    schema_json = json.dumps(BACKGROUND_SCHEMA, ensure_ascii=False, separators=(",", ":"))
    valid_backgrounds = ", ".join(BACKGROUND)
    return (
        f"Job posting:\n{job_text}\n\n"
        f"Available backgrounds:\n{BACKGROUND_PAYLOAD}\n\n"
        f"Valid background names: {valid_backgrounds}\n\n"
        f"Return ONLY valid JSON matching this schema:\n{schema_json}"
    )


# ── Pipeline functions ────────────────────────────────────────────────────────

def extract_job_via_oracle(job_text: str, url: str, client: OpenAI, model: str) -> Dict[str, str]:
    user_content = build_job_user_content(job_text)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": JOB_PROMPT},
            {"role": "user", "content": user_content},
        ],
        temperature=0.0,
        stream=False,
    )

    raw = response.choices[0].message.content.strip()
    job_data = parse_oracle_json(unicode_to_utf8(raw))
    job_data = _validate_job_data(job_data, url)

    job_data["location"] = clean_city_location(job_data["location"])
    return job_data


def write_sentence_via_oracle(job_text: str, url: str, client: OpenAI, model: str) -> Dict[str, str]:
    user_content = build_sentence_user_content(job_text, url)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SENTENCE_PROMPT},
            {"role": "user", "content": user_content},
        ],
        temperature=0.4,
        stream=False,
    )

    raw = response.choices[0].message.content.strip()

    try:
        result = parse_oracle_json(raw)
        result = _validate_sentence_data(result)
    except Exception:
        repair_prompt = (
            "Your previous answer was invalid or low quality.\n"
            "Return ONLY valid JSON matching the required schema.\n"
            "Do not add any extra text.\n"
            "Make 'sentence_first_paragraph' specific, challenge-led, human-sounding, "
            "and directly tied to the company challenge and the work of the role.\n"
            "Avoid generic phrases like 'innovative solutions', 'complex business issues', "
            "'passionate about', or 'fast-paced environment'."
        )

        repair_response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SENTENCE_PROMPT},
                {"role": "user", "content": user_content},
                {"role": "assistant", "content": raw},
                {"role": "user", "content": repair_prompt},
            ],
            temperature=0.1,
            stream=False,
        )

        repaired_raw = repair_response.choices[0].message.content.strip()
        result = parse_oracle_json(repaired_raw)
        result = _validate_sentence_data(result)

    phrase = result.get("sentence_first_paragraph", "").strip().lower()

    forbidden_fragments = [
        "innovative solutions",
        "complex business issues",
        "passionate about",
        "dynamic environment",
        "fast-paced environment",
        "telecommunications innovation",
        "cutting-edge",
        "addressing needs",
    ]

    if (
        len(phrase.split()) < 10
        or any(fragment in phrase for fragment in forbidden_fragments)
    ):
        quality_repair_prompt = (
            "Rewrite ONLY the field 'sentence_first_paragraph' and keep all other fields intact.\n"
            "The phrase must be 10-20 words, human-written, and grounded in:\n"
            "1. the company's challenge,\n"
            "2. the work this job is meant to do,\n"
            "3. the company context.\n"
            "It must sound like a real reason for applying, not a generic summary.\n"
            "Return ONLY valid JSON."
        )

        quality_response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SENTENCE_PROMPT},
                {"role": "user", "content": user_content},
                {"role": "assistant", "content": json.dumps(result, ensure_ascii=False)},
                {"role": "user", "content": quality_repair_prompt},
            ],
            temperature=0.4,
            stream=False,
        )

        quality_raw = quality_response.choices[0].message.content.strip()
        result = parse_oracle_json(quality_raw)
        result = _validate_sentence_data(result)

    return result


def select_projects_via_oracle(job_text: str, client: OpenAI, model: str) -> dict:
    user_content = build_project_user_content(job_text)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": PROJECTS_PROMPT},
            {"role": "user", "content": user_content},
        ],
        temperature=0.2,
        stream=False,
    )

    raw = response.choices[0].message.content.strip()
    result = parse_oracle_json(raw)
    return _validate_project_data(result)


def select_background_via_oracle(job_text: str, client: OpenAI, model: str) -> dict:
    user_content = build_background_user_content(job_text)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": BACKGROUND_PROMPT},
            {"role": "user", "content": user_content},
        ],
        temperature=0.2,
        stream=False,
    )

    raw = response.choices[0].message.content.strip()
    result = parse_oracle_json(raw)
    return _validate_background_data(result)


# ── Main pipeline ─────────────────────────────────────────────────────────────

def run_oracle_pipeline(
    url: str,
    *,
    extract: bool = False,
    tailor_sentence: bool = False,
    select_projects: bool = False,
    select_background: bool = False,
    client: OpenAI | None = None,
    model: str | None = None
) -> dict:
    """
    Run the oracle pipeline.

    Args:
        url:                Job posting URL.
        extract:            Extract structured job metadata.
        tailor_sentence:    Craft tailored cover letter slots.
        select_projects:    Select 3 most relevant projects for the CV.
        select_background:  Select 3 most relevant background skills for cover letter.
        client:             Optional pre-built API client (useful for tests).
        model:              What the user needs, want to use

    Returns:
        dict: Merged results from all enabled pipeline stages.
    """

    if not any([extract, tailor_sentence, select_projects, select_background]):
        raise ValueError(
            "At least one mode must be enabled: extract, tailor_sentence, "
            "select_projects, select_background"
        )

    client = client or build_llm_client()
    model = model or get_default_model()
    job_text = scrape_job_text(url)

    result: dict = {}

    if extract:
        job_data = extract_job_via_oracle(job_text, url, client, model)
        if not isinstance(job_data, dict):
            raise ValueError("extract_job_via_oracle() must return a dict")
        result.update(job_data)

    if tailor_sentence:
        sentence_info = write_sentence_via_oracle(job_text, url, client, model)

        if not isinstance(sentence_info, dict):
            raise ValueError("write_sentence_via_oracle() must return a dict")
        result.update({k: v for k, v in sentence_info.items() if k not in result})

    if select_projects:
        project_info = select_projects_via_oracle(job_text, client, model)
        project_data = normalize_project_selection(project_info)

        if not isinstance(project_data, dict):
            raise ValueError("select_projects_via_oracle() must return a dict")

        result.update(
            {
                "project_one": project_data.get("project_one", ""),
                "project_two": project_data.get("project_two", ""),
                "project_three": project_data.get("project_three", ""),
                "reason_selected_1": project_data.get("reason_selected_1", ""),
                "reason_selected_2": project_data.get("reason_selected_2", ""),
                "reason_selected_3": project_data.get("reason_selected_3", ""),
            }
        )

    if select_background:
        background_dict = select_background_via_oracle(job_text, client, model)
        background_info = dict_values_to_sentence(background_dict, ", ")
        if not isinstance(background_info, str):
            raise ValueError("select_background_via_oracle() must return a str of backgrounds")
        result["your_background"] = background_info

    return result


console = Console()


def run_oracle_flow(
    url: str,
    csv_path: str,
    extract: bool,
    tailor_sentence: bool,
    select_projects: bool,
    select_background: bool,
) -> None:
    _validate_flags(extract, tailor_sentence, select_projects, select_background)

    _show_active_modes(
        extract=extract,
        tailor_sentence=tailor_sentence,
        select_projects=select_projects,
        select_background=select_background,
    )

    try:
        with console.status(
            f"[{rgb(COMMAND_COLORS['oracle'])}][bold]The Oracle is working ...[/bold][/{rgb(COMMAND_COLORS['oracle'])}]"
        ):
            result = run_oracle_pipeline(
                url=url,
                extract=extract,
                tailor_sentence=tailor_sentence,
                select_projects=select_projects,
                select_background=select_background,
            )
    except ValueError as exc:
        console.print(f"[bold red]{exc}[/bold red]")
        raise typer.Exit(code=1) from exc
    except Exception as exc:
        console.print(f"[bold red]Oracle failed: {exc}[/bold red]")
        raise typer.Exit(code=1) from exc

    if not isinstance(result, dict) or not result:
        console.print("[bold red]Oracle returned an empty or invalid result.[/bold red]")
        raise typer.Exit(code=1)

    console.print()
    _display_oracle_result(
        result=result,
        extract=extract,
        tailor_sentence=tailor_sentence,
        select_projects=select_projects,
        select_background=select_background,
    )

    editable = {k: v for k, v in result.items() if k not in NON_EDITABLE}
    if editable:
        console.print(
            f"Would you like to [{rgb(COMMAND_COLORS['update'])}]modify[/{rgb(COMMAND_COLORS['update'])}] this information?"
        )

    if typer.confirm("Modify fields", default=False):
        updated = edit_oracle_dict(editable)
        result.update(updated)
        _display_updated_fields(updated)


def _validate_flags(
    extract: bool,
    tailor_sentence: bool,
    select_projects: bool,
    select_background: bool,
) -> None:
    if not any([extract, tailor_sentence, select_projects, select_background]):
        console.print(
            "[bold red]Use at least one flag: --extract, --tailor_sentence, "
            "--select_projects, --select_background[/bold red]"
        )
        raise typer.Exit(code=1)


# ── Test Oracle ─────────────────────────────────────────────────────────────


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
