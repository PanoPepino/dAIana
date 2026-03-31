from openai import OpenAI  # or TO BE changed for other client if required
from daiana.utils.for_oracle import *
from daiana.utils.prompts import JOB_PROMPT, SENTENCE_PROMPT, SENTENCE_SCHEMA


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
        temperature=0.2
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
