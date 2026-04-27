# This file is used to check whether your prompts are correctly read by Oracle.

import json
from daiana.utils.prompt_loader import loader


# =============================================================================
# LOADED FROM prompts/
# =============================================================================

_background_raw = loader.load("background/background_payload")
_background_schema_raw = loader.load("background/background_schema")
_sentence_schema_raw = loader.load("sentence/sentence_schema")
_projects_schema_raw = loader.load("projects/projects_schema")
_job_schema_raw = loader.load("job/job_schema")
_project_name_latex_raw = loader.load("projects/projects_name_to_latex")

JOB_PROMPT = loader.load("job/job_prompt")
SENTENCE_PROMPT = loader.load("sentence/sentence_prompt")
PROJECTS_PROMPT = loader.load("projects/projects_prompt")
BACKGROUND_PROMPT = loader.load("background/background_prompt")

PROJECTS_PAYLOAD = loader.load("projects/projects_payload")
BACKGROUND_PAYLOAD = _background_raw

CAREERS_CONFIG = json.loads(loader.load("career/careers"))
CAREERS = CAREERS_CONFIG["options"]

SENTENCE_SCHEMA = json.loads(_sentence_schema_raw)
PROJECTS_SCHEMA = json.loads(_projects_schema_raw)
BACKGROUND_SCHEMA = json.loads(_background_schema_raw)
JOB_SCHEMA = json.loads(_job_schema_raw)
JOB_SCHEMA["career"] = "|".join(CAREERS)

PROJECT_NAME_TO_LATEX = json.loads(_project_name_latex_raw)


# =============================================================================
# PARSE BACKGROUND LIST
# =============================================================================

def _parse_background_list(raw: str) -> list[str]:
    """Extract bullet-point items from background payload markdown."""
    return [
        line.lstrip("- ").strip()
        for line in raw.splitlines()
        if line.strip().startswith("-")
    ]


BACKGROUND = _parse_background_list(_background_raw)
