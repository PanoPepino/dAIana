import os
import json
import re


from daiana.utils.for_oracle import scrape_job_text
from openai import OpenAI
from dotenv import load_dotenv
from openai import OpenAI  # or TO BE changed for other client if required
from daiana.utils.for_oracle import *
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
        raise ValueError(
            f"Oracle returned invalid JSON: {exc}\nRaw: {raw}"
        ) from exc

    if not isinstance(data, dict):
        raise ValueError("Oracle JSON must decode into a dictionary")

    return data


def extract_job_via_oracle(job_text: str,
                           url: str,
                           client: OpenAI) -> Dict[str, str]:

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
        "2) Location (i.e. city) must be only the city, in UTF‑8, no Unicode escapes.\n"
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
    job_data = json.loads(decoded)

    # Cleanup location
    job_data["location"] = clean_city_location(job_data["location"])

    return job_data


def write_sentence_via_oracle(job_text: str,
                              url: str,
                              client: OpenAI) -> Dict[str, str]:

    schema_json = json.dumps(SENTENCE_SCHEMA, ensure_ascii=False, separators=(",", ":"))

    user_content = (
        f"Job advertisement URL: {url}\n\n"
        f"Job advertisement text:\n{job_text}\n\n"
        "Instructions:\n"
        "Step 1 — Read the job text carefully and fill 'evidence_challenges' with 1-3 "
        "specific challenges or priorities the COMPANY faces, using words from the text.\n"
        "Step 2 — Fill 'role_impact_area' with what this specific role is meant to solve.\n"
        "Step 3 — Write 'sentence' using ONLY what you found in Steps 1 and 2.\n"
        "Step 4 — If the text contains NO clear company challenge, set 'sentence' to "
        "an empty string and explain in 'evidence_challenges' why.\n\n"
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

    try:
        result: Dict[str, str] = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"Oracle returned invalid JSON: {e}\nRaw: {raw}")

    sentence = result.get("sentence", "")
    if sentence and not sentence.startswith("I think I can meaningfully contribute to"):
        raise ValueError(
            f"Sentence prefix mismatch. Got:\n{sentence}"
        )

    return result


def build_perplexity_client() -> OpenAI:
    """
    Func to call the API service. Probably will be enhanced in future.

    Returns:
        OpenAI: the AI ready to eat a prompt
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
    The oracle pipeline. You can pass two flags at the moment to oracle. One for extract info of the job position and another one to tailor parts of your cover letter based on the information scrapped.

    Args:
        url (str): The url to the job position info.
        extract (bool, optional): The flag to simply scrap and extract info. Defaults to False.
        tailor_cl (bool, optional): The flag to scrap and craft a simple tailored sentence on how you can contribute to the job position. Defaults to False.
        client (OpenAI | None, optional): _description_. Defaults to None.


    Returns:
        dict: The extracted/crafted information
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
