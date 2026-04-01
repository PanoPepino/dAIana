import os
import json
import re

from typing import Dict
from daiana.utils.for_oracle import scrape_job_text, unicode_to_utf8, clean_city_location, edit_oracle_dict
from openai import OpenAI
from dotenv import load_dotenv
from daiana.utils.prompts import JOB_PROMPT, SENTENCE_PROMPT, SENTENCE_SCHEMA


def _clean_llm_json(raw: str) -> str:
    if not isinstance(raw, str):
        raise ValueError("Oracle response must be a string before JSON parsing")

    cleaned = raw.strip()

    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```$", "", cleaned)

    cleaned = cleaned.replace("\u00a0", " ")
    cleaned = cleaned.strip()

    return cleaned


def parse_oracle_json(raw: str) -> dict:
    cleaned = _clean_llm_json(raw)

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        # Second attempt: extract first {...} block
        brace_match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if brace_match:
            try:
                data = json.loads(brace_match.group())
            except json.JSONDecodeError:
                raise ValueError(
                    f"Oracle returned invalid JSON: {exc}\nRaw: {raw}"
                ) from exc
        else:
            raise ValueError(
                f"Oracle returned invalid JSON: {exc}\nRaw: {raw}"
            ) from exc

    if not isinstance(data, dict):
        raise ValueError("Oracle JSON must decode into a dictionary")

    return data


_REQUIRED_JOB_FIELDS = ("job_position", "company_name", "career", "location", "job_link")
_VALID_CAREERS = {"data", "rd", "quant"}


def _validate_job_data(data: dict, url: str) -> dict:
    """Ensure all required fields exist and career is valid. Fill missing with safe defaults."""
    for field in _REQUIRED_JOB_FIELDS:
        if field not in data or data[field] is None:
            data[field] = ""
    if not data["job_link"]:
        data["job_link"] = url
    if data["career"] not in _VALID_CAREERS:
        data["career"] = "rd"  # safe default
    return data


def extract_job_via_oracle(job_text: str, url: str, client: OpenAI) -> Dict[str, str]:

    schema = {
        "job_position": "",
        "company_name": "",
        "career": "data|rd|quant",
        "location": "",
        "job_link": url,
    }

    schema_json = json.dumps(schema, ensure_ascii=False, separators=(",", ":"))

    user_content = (
        f"Extract for LaTeX cover letter from job text:\n"
        f"Text: {job_text}\n\n"
        f"Output ONLY as JSON using this exact schema:\n"
        f"{schema_json}\n\n"
        "Rules again:\n"
        "1) Job position must be in English.\n"
        "2) Location (i.e. city) must be only the city, in UTF-8, no Unicode escapes.\n"
        "3) For career, choose exactly one of \"data\", \"rd\", or \"quant\"."
    )

    response = client.chat.completions.create(
        model="sonar",
        messages=[
            {"role": "system", "content": JOB_PROMPT},
            {"role": "user",   "content": user_content},
        ],
        temperature=0.0,
    )

    raw = response.choices[0].message.content.strip()
    decoded = unicode_to_utf8(raw)
    job_data = parse_oracle_json(decoded)
    job_data = _validate_job_data(job_data, url)
    job_data["location"] = clean_city_location(job_data["location"])

    return job_data


_REQUIRED_SENTENCE_FIELDS = (
    "company_name", "career", "challenge_area",
    "business_domain", "sentence_first_paragraph"
)


def _validate_sentence_data(data: dict) -> dict:
    """Ensure all sentence schema fields exist. Fill missing with empty string."""
    for field in _REQUIRED_SENTENCE_FIELDS:
        if field not in data or data[field] is None:
            data[field] = ""
    return data


def write_sentence_via_oracle(job_text: str, url: str, client: OpenAI) -> Dict[str, str]:

    schema_json = json.dumps(SENTENCE_SCHEMA, ensure_ascii=False, separators=(",", ":"))

    user_content = (
        f"Job advertisement URL: {url}\n\n"
        f"Job advertisement text:\n{job_text}\n\n"
        "Instructions:\n"
        "Step 1 — Read the job text carefully and fill 'challenge_area' with 1-3 "
        "specific challenges or priorities the COMPANY faces, using words from the text.\n"
        "Step 2 — Fill 'business_domain' with what this specific role is meant to solve.\n"
        "Step 3 — Write 'sentence_first_paragraph' using ONLY what you found in Steps 1 and 2.\n"
        "Step 4 — If the text contains NO clear company challenge, set 'sentence_first_paragraph' to "
        "an empty string and explain in 'challenge_area' why.\n\n"
        f"Output ONLY valid JSON using this exact schema:\n{schema_json}"
    )

    response = client.chat.completions.create(
        model="sonar-pro",
        messages=[
            {"role": "system", "content": SENTENCE_PROMPT},
            {"role": "user",   "content": user_content},
        ],
        temperature=0.25
    )

    raw = response.choices[0].message.content.strip()
    result: Dict[str, str] = parse_oracle_json(raw)
    result = _validate_sentence_data(result)

    return result


def build_perplexity_client() -> OpenAI:
    """
    Build and return the Perplexity API client.

    Returns:
        OpenAI: the AI client ready to process prompts.
    """
    load_dotenv()
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        raise ValueError("PERPLEXITY_API_KEY not found in environment or .env")
    return OpenAI(
        api_key=api_key,
        base_url="https://api.perplexity.ai",
    )


def run_oracle_pipeline(
        url: str,
        *,
        extract: bool = False,
        tailor_cl: bool = False,
        client: OpenAI | None = None) -> dict:
    """
    Run the oracle pipeline to extract job info and/or craft tailored cover letter sentences.

    Args:
        url (str): The URL to the job position.
        extract (bool): Scrape and extract structured job info.
        tailor_cl (bool): Scrape and craft a tailored cover letter sentence.
        client (OpenAI | None): Optional pre-built API client (useful for tests).

    Returns:
        dict: The extracted/crafted information.
    """
    if not extract and not tailor_cl:
        raise ValueError("At least one mode must be enabled: extract or tailor_cl")

    client = client or build_perplexity_client()
    job_text = scrape_job_text(url)

    result: dict = {}

    if extract:
        job_data = extract_job_via_oracle(job_text, url, client)
        if not isinstance(job_data, dict):
            raise ValueError("extract_job_via_oracle() must return a dict")
        result.update(job_data)

    if tailor_cl:
        sentence_info = write_sentence_via_oracle(job_text, url, client)
        if not isinstance(sentence_info, dict):
            raise ValueError("write_sentence_via_oracle() must return a dict")
        result.update(sentence_info)

    return result
