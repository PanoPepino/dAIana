
"""
This file contains all the logic to use API requests to the given AI and to display the results in your terminal.   
"""

import json
import typer

from rich.console import Console
from typing import Dict
from openai import OpenAI


from daiana.utils.colors import COMMAND_COLORS
from daiana.utils.ui import (
    rgb,
    _display_oracle_result,
    _display_updated_fields,
    _show_active_modes)
from daiana.utils.for_oracle import (
    dict_values_to_sentence,
    edit_oracle_dict,
    parse_oracle_json,
    unicode_to_utf8,
    scrape_job_text,
    clean_city_location,
    _validate_job_data,
    _validate_project_data,
    _validate_sentence_data,
    _validate_background_data,
    build_perplexity_client,
    normalize_project_selection,

)
from daiana.utils.prompts import (
    BACKGROUND,
    BACKGROUND_PROMPT,
    JOB_PROMPT,
    SENTENCE_PROMPT,
    SENTENCE_SCHEMA,
    PROJECT_PROMPT,
    PROJECT_SELECTION_SCHEMA,
    PROJECTS_PAYLOAD,
    PROJECT_NAME_TO_LATEX,
    BACKGROUND_PAYLOAD,
    BACKGROUND_SELECTION_SCHEMA
)

# ── Pipeline functions ────────────────────────────────────────────────────────


def extract_job_via_oracle(job_text: str, url: str, client: OpenAI) -> Dict[str, str]:
    schema = {
        "job_position": "",
        "company_name": "",
        "career":       "data|rd|quant",  # To be modified in future
        "location":     "",
        "job_link":     url,
    }
    schema_json = json.dumps(schema, ensure_ascii=False, separators=(",", ":"))
    user_content = (
        f"Extract for LaTeX cover letter from job text:\n{job_text}\n\n"
        f"Output ONLY as JSON using this exact schema:\n{schema_json}\n\n"
        "Rules:\n"
        "1) job_position must be in English.\n"
        "2) location: city only, UTF-8 chars, no postal codes.\n"
        "3) career: exactly one of 'data', 'rd', or 'quant'."  # To be modified in future
    )
    response = client.chat.completions.create(
        model="sonar",
        messages=[
            {"role": "system", "content": JOB_PROMPT},
            {"role": "user",   "content": user_content},
        ],
        temperature=0.0,
        stream=False
    )
    raw = response.choices[0].message.content.strip()
    job_data = parse_oracle_json(unicode_to_utf8(raw))
    job_data = _validate_job_data(job_data, url)
    job_data["location"] = clean_city_location(job_data["location"])
    return job_data


def write_sentence_via_oracle(job_text: str, url: str, client: OpenAI) -> Dict[str, str]:
    schema_json = json.dumps(SENTENCE_SCHEMA, ensure_ascii=False, separators=(",", ":"))
    user_content = (
        f"Job advertisement URL: {url}\n\n"
        f"Job advertisement text:\n{job_text}\n\n"
        "From the ad above, fill the JSON schema:\n"
        "1. 'challenge_area' — 1-3 specific challenges the COMPANY faces, verbatim from the ad.\n"
        "2. 'business_domain'— the domain this role exists to solve.\n"
        "3. 'sentence_first_paragraph'— build as [DOMAIN] and [TENSION] [CONTEXT], 15-25 words.\n"
        "   If no concrete challenge found: set to \"\" and explain in 'challenge_area'.\n\n"
        f"Output ONLY valid JSON using this exact schema:\n{schema_json}"
    )
    response = client.chat.completions.create(
        model="sonar-pro",
        messages=[
            {"role": "system", "content": SENTENCE_PROMPT},
            {"role": "user",   "content": user_content},
        ],
        temperature=0.5,
        stream=False,
    )
    raw = response.choices[0].message.content.strip()
    result = parse_oracle_json(raw)
    return _validate_sentence_data(result)


def select_projects_via_oracle(job_text: str, client: OpenAI) -> dict:
    schema_json = json.dumps(PROJECT_SELECTION_SCHEMA, ensure_ascii=False, separators=(",", ":"))
    user_content = (
        f"Job posting:\n{job_text}\n\n"
        f"{PROJECTS_PAYLOAD}\n"
        f"Valid names: {', '.join(PROJECT_NAME_TO_LATEX.keys())}\n\n"
        f"Output ONLY valid JSON using this exact schema:\n{schema_json}"
    )
    response = client.chat.completions.create(
        model="sonar-pro",
        messages=[
            {"role": "system", "content": PROJECT_PROMPT},
            {"role": "user",   "content": user_content},
        ],
        temperature=0.0,
        stream=False,
    )
    raw = response.choices[0].message.content.strip()
    result = parse_oracle_json(raw)
    return _validate_project_data(result)


def select_background_via_oracle(job_text: str, client: OpenAI) -> dict:
    schema_json = json.dumps(
        BACKGROUND_SELECTION_SCHEMA,
        ensure_ascii=False,
        separators=(",", ":"),
    )

    user_content = (
        f"Job posting:\n{job_text}\n\n"
        f"{BACKGROUND_PAYLOAD}\n"
        f"Valid background names: {', '.join(BACKGROUND)}\n\n"
        f"Output ONLY valid JSON using this exact schema:\n{schema_json}"
    )

    response = client.chat.completions.create(
        model="sonar",
        messages=[
            {"role": "system", "content": BACKGROUND_PROMPT},
            {"role": "user", "content": user_content},
        ],
        temperature=0.0,
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
) -> dict:
    """
    Run the oracle pipeline.

    Args:
            url:                Job posting URL.
            extract:            Extract structured job metadata.
            tailor_sentence:    Craft tailored cover letter slots (background + challenge).
            select_projects:    Select 3 most relevant projects for the CV.
            select_background:  Select 3 most relevant background skills for cover letter.
            client:             Optional pre-built API client (useful for tests).

    Returns:
        dict: Merged results from all enabled pipeline stages.
    """

    if not any([extract, tailor_sentence, select_projects, select_background]):
        raise ValueError("At least one mode must be enabled: extract, tailor_sentence, select_projects, select_background")

    client = client or build_perplexity_client()
    job_text = scrape_job_text(url)   # scraped once, reused by all stages

    result: dict = {}

    if extract:
        job_data = extract_job_via_oracle(job_text, url, client)
        if not isinstance(job_data, dict):
            raise ValueError("extract_job_via_oracle() must return a dict")
        result.update(job_data)

    if tailor_sentence:
        sentence_info = write_sentence_via_oracle(job_text, url, client)
        if not isinstance(sentence_info, dict):
            raise ValueError("write_sentence_via_oracle() must return a dict")
        result.update(sentence_info)

    if select_projects:
        project_info = select_projects_via_oracle(job_text, client)
        project_data = normalize_project_selection(project_info)

        if not isinstance(project_data, dict):
            raise ValueError("select_projects_via_oracle() must return a dict")
        result.update(
            {
                "project_one": project_data.get("project_one", ""),
                "project_two": project_data.get("project_two", ""),
                "project_three": project_data.get("project_three", ""),
                "reason_name_1": project_data.get("reason_name_1", ""),
                "reason_name_2": project_data.get("reason_name_2", ""),
                "reason_name_3": project_data.get("reason_name_3", ""),
            }
        )
    if select_background:
        background_dic = select_background_via_oracle(job_text, client)
        background_info = dict_values_to_sentence(background_dic, ', ')
        if not isinstance(background_info, str):
            raise ValueError("select_background_via_oracle() must return a str of backgrounds")
        result['your_background'] = background_info

    return result


console = Console()


NON_EDITABLE = {
    "reasons",
    "challenge_area",
    "business_domain",
    "reason_name_1",
    "reason_name_2",
    "reason_name_3",
}


def run_oracle_flow(
    url: str,
    csv_path: str,
    extract: bool,
    tailor_sentence: bool,
    select_projects: bool,
    select_background: bool,
) -> None:
    _validate_flags(extract, tailor_sentence, select_projects, select_background)
    active = _show_active_modes(
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
            "[bold red]Use at least one flag: --extract, --tailor_sentence, --select_projects, --select_background[/bold red]"
        )
        raise typer.Exit(code=1)
