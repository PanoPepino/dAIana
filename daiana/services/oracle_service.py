"""Oracle service — replaces core/oracler.py.

All LLM calls, prompt composition, and oracle pipeline logic live here.
No module-level file I/O; everything is lazy via PromptRepository.
"""
from __future__ import annotations

import json
import re

from openai import OpenAI
from rich.console import Console
from rich.prompt import Prompt

import typer

from daiana.config.settings import load_settings
from daiana.infra.llm_client import build_client
from daiana.infra.prompt_repository import make_prompt_repository, PromptRepository
from daiana.infra.scraper import scrape_job_text
from daiana.domain.validation import (
    validate_job_data,
    validate_sentence_data,
    validate_project_data,
    validate_background_data,
)
from daiana.utils.constants import NON_EDITABLE
from daiana.utils.design.colors import COMMAND_COLORS
from daiana.utils.design.ui import rgb, _display_oracle_result, _display_updated_fields, _show_active_modes

console = Console()


# ── JSON helpers ──────────────────────────────────────────────────────────────

def _clean_llm_json(raw: str) -> str:
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    return cleaned.replace("\u00a0", " ").strip()


def parse_oracle_json(raw: str) -> dict:
    cleaned = _clean_llm_json(raw)
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        m = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if m:
            try:
                data = json.loads(m.group())
            except json.JSONDecodeError:
                raise ValueError(f"Oracle returned invalid JSON: {exc}\nRaw: {raw}") from exc
        else:
            raise ValueError(f"Oracle returned invalid JSON: {exc}\nRaw: {raw}") from exc
    if not isinstance(data, dict):
        raise ValueError("Oracle JSON must decode into a dictionary")
    return data


def unicode_to_utf8(raw: str) -> str:
    try:
        return raw.encode("latin1").decode("unicode_escape").encode("latin1").decode("utf-8")
    except Exception:
        return raw


def clean_city_location(loc: str) -> str:
    if not loc.strip():
        return "Unknown"
    parts = [p.strip() for p in loc.split(",") if p.strip()]
    return parts[-1] if parts else "Unknown"


def dict_values_to_sentence(d: dict, sep: str = ", ") -> str:
    values = [str(v) for v in d.values() if v not in (None, "")]
    if not values:
        return ""
    if len(values) == 1:
        return values[0]
    if len(values) == 2:
        return " and ".join(values)
    return f"{sep.join(values[:-1])} and {values[-1]}"


def normalize_project_selection(selection: dict) -> dict:
    return {
        "project_one": selection.get("selected_1", ""),
        "project_two": selection.get("selected_2", ""),
        "project_three": selection.get("selected_3", ""),
        "reason_selected_1": selection.get("reason_selected_1", ""),
        "reason_selected_2": selection.get("reason_selected_2", ""),
        "reason_selected_3": selection.get("reason_selected_3", ""),
    }


def edit_oracle_dict(job: dict) -> dict:
    console.print()
    console.print(f"[{rgb(COMMAND_COLORS['update'])}]Review each field (Enter to keep).[/{rgb(COMMAND_COLORS['update'])}]")
    console.print()
    for key in job.keys():
        current = str(job.get(key) or "")
        new_value = Prompt.ask(f"[bold white]{key:14}[/bold white]", default=current, show_default=True).strip()
        if new_value:
            job[key] = new_value
    return job


# ── LLM request helpers ───────────────────────────────────────────────────────

def _chat(client: OpenAI, model: str, system: str, user: str, temperature: float = 0.0) -> str:
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        temperature=temperature,
        stream=False,
    )
    return resp.choices[0].message.content.strip()


# ── Pipeline step functions ───────────────────────────────────────────────────

def extract_job(job_text: str, url: str, client: OpenAI, model: str, prompts: PromptRepository) -> dict:
    schema = prompts.job_schema()
    careers = prompts.careers()
    user = (
        f"Job text:\n{job_text}\n\nReturn ONLY valid JSON matching:\n{json.dumps(schema)}\n\n"
        f"Rules:\n1) job_position in English.\n2) location: city only.\n"
        f"3) career MUST be one of: {'|'.join(careers)}.\nDo not invent careers."
    )
    raw = _chat(client, model, prompts.text("job/job_prompt"), user)
    data = validate_job_data(parse_oracle_json(unicode_to_utf8(raw)), url)
    data["location"] = clean_city_location(data["location"])
    return data


def write_sentence(job_text: str, url: str, client: OpenAI, model: str, prompts: PromptRepository) -> dict:
    schema = json.dumps(prompts.as_json("sentence/sentence_schema"))
    system = prompts.text("sentence/sentence_prompt")
    user = f"Job URL:\n{url}\n\nJob text:\n{job_text}\n\nFill this JSON schema exactly:\n{schema}"

    raw = _chat(client, model, system, user, temperature=0.4)
    try:
        result = validate_sentence_data(parse_oracle_json(raw))
    except Exception:
        repair = (
            "Your previous answer was invalid. Return ONLY valid JSON matching the required schema.\n"
            "Make 'sentence_first_paragraph' specific, challenge-led, human-sounding."
        )
        resp2 = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
                {"role": "assistant", "content": raw},
                {"role": "user", "content": repair},
            ],
            temperature=0.1, stream=False,
        )
        result = validate_sentence_data(parse_oracle_json(resp2.choices[0].message.content.strip()))
    return result


def select_projects(job_text: str, client: OpenAI, model: str, prompts: PromptRepository) -> dict:
    schema = json.dumps(prompts.as_json("projects/projects_schema"))
    valid_names = ", ".join(prompts.as_json("projects/projects_name_to_latex").keys())
    payload = prompts.text("projects/projects_payload")
    user = (
        f"Job posting:\n{job_text}\n\nAvailable projects:\n{payload}\n\n"
        f"Valid names: {valid_names}\n\nReturn ONLY valid JSON matching:\n{schema}"
    )
    raw = _chat(client, model, prompts.text("projects/projects_prompt"), user, temperature=0.2)
    valid_set = set(prompts.as_json("projects/projects_name_to_latex").keys())
    return validate_project_data(parse_oracle_json(raw), valid_set)


def select_background(job_text: str, client: OpenAI, model: str, prompts: PromptRepository) -> dict:
    schema = json.dumps(prompts.as_json("background/background_schema"))
    payload = prompts.text("background/background_payload")
    bg_list = prompts.background_list()
    valid_names = ", ".join(bg_list)
    user = (
        f"Job posting:\n{job_text}\n\nAvailable backgrounds:\n{payload}\n\n"
        f"Valid background names: {valid_names}\n\nReturn ONLY valid JSON matching:\n{schema}"
    )
    raw = _chat(client, model, prompts.text("background/background_prompt"), user, temperature=0.2)
    return validate_background_data(parse_oracle_json(raw), set(bg_list))


# ── Main pipeline ─────────────────────────────────────────────────────────────

def run_oracle_pipeline(
    url: str,
    *,
    extract: bool = False,
    tailor_sentence: bool = False,
    select_projects_flag: bool = False,
    select_background_flag: bool = False,
    client: OpenAI | None = None,
    model: str | None = None,
) -> dict:
    if not any([extract, tailor_sentence, select_projects_flag, select_background_flag]):
        raise ValueError("At least one mode must be enabled.")

    settings = load_settings()
    prompts = make_prompt_repository()
    _client = client or build_client(settings)
    _model = model or settings.model
    job_text = scrape_job_text(url)
    result: dict = {}

    if extract:
        result.update(extract_job(job_text, url, _client, _model, prompts))
    if tailor_sentence:
        sentence = write_sentence(job_text, url, _client, _model, prompts)
        result.update({k: v for k, v in sentence.items() if k not in result})
    if select_projects_flag:
        project_data = normalize_project_selection(select_projects(job_text, _client, _model, prompts))
        result.update(project_data)
    if select_background_flag:
        bg_dict = select_background(job_text, _client, _model, prompts)
        result["your_background"] = dict_values_to_sentence(bg_dict)

    return result


def run_oracle_flow(
    url: str,
    csv_path: str,
    extract: bool,
    tailor_sentence: bool,
    select_projects: bool,
    select_background: bool,
) -> None:
    if not any([extract, tailor_sentence, select_projects, select_background]):
        console.print("[bold red]Use at least one flag: --extract, --tailor_sentence, --select_projects, --select_background[/bold red]")
        raise typer.Exit(code=1)

    _show_active_modes(
        extract=extract, tailor_sentence=tailor_sentence,
        select_projects=select_projects, select_background=select_background,
    )

    try:
        with console.status(f"[{rgb(COMMAND_COLORS['oracle'])}][bold]The Oracle is working ...[/bold][/{rgb(COMMAND_COLORS['oracle'])}]"):
            result = run_oracle_pipeline(
                url=url,
                extract=extract,
                tailor_sentence=tailor_sentence,
                select_projects_flag=select_projects,
                select_background_flag=select_background,
            )
    except (ValueError, Exception) as exc:
        console.print(f"[bold red]Oracle failed: {exc}[/bold red]")
        raise typer.Exit(code=1) from exc

    if not isinstance(result, dict) or not result:
        console.print("[bold red]Oracle returned an empty or invalid result.[/bold red]")
        raise typer.Exit(code=1)

    console.print()
    _display_oracle_result(
        result=result, extract=extract, tailor_sentence=tailor_sentence,
        select_projects=select_projects, select_background=select_background,
    )

    editable = {k: v for k, v in result.items() if k not in NON_EDITABLE}
    if editable and typer.confirm("Modify fields", default=False):
        updated = edit_oracle_dict(editable)
        result.update(updated)
        _display_updated_fields(updated)
