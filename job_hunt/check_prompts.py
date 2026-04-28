import os

from daiana.utils.prompt_loader import loader
from daiana.utils.prompts import (
    JOB_PROMPT,
    SENTENCE_PROMPT,
    PROJECTS_PROMPT,
    BACKGROUND_PROMPT,
    PROJECTS_PAYLOAD,
    BACKGROUND_PAYLOAD,
    BACKGROUND,
    PROJECT_NAME_TO_LATEX,
    SENTENCE_SCHEMA,
    PROJECTS_SCHEMA,
    BACKGROUND_SCHEMA,
    JOB_SCHEMA,
)


SEP = "-" * 140


def check(name, value):
    if isinstance(value, str):
        preview = value[:80].replace("\n", " ")
        print(f"✅ {name}: {len(value)} chars | '{preview}...'")
    elif isinstance(value, list):
        first = value[0] if value else ""
        print(f"✅ {name}: {len(value)} items | first: '{first}'")
    elif isinstance(value, dict):
        keys = list(value.keys())
        print(f"✅ {name}: {len(keys)} keys | {keys}")
    else:
        print(f"❌ {name}: unexpected type {type(value)}")


print("")
print(SEP)
print("DAIANA PROMPT LOADER — DIAGNOSTIC")
print(SEP)
print(f"DAIANA_JOB_HUNT_DIR : {os.getenv('DAIANA_JOB_HUNT_DIR', '<not set>')}")
print(f"Prompts dir         : {loader.prompts_dir}")
print(SEP)

check("JOB_PROMPT", JOB_PROMPT)
check("SENTENCE_PROMPT", SENTENCE_PROMPT)
check("PROJECTS_PROMPT", PROJECTS_PROMPT)
check("BACKGROUND_PROMPT", BACKGROUND_PROMPT)

check("PROJECTS_PAYLOAD", PROJECTS_PAYLOAD)
check("BACKGROUND_PAYLOAD", BACKGROUND_PAYLOAD)
check("BACKGROUND (parsed list)", BACKGROUND)

check("SENTENCE_SCHEMA", SENTENCE_SCHEMA)
check("JOB_SCHEMA", JOB_SCHEMA)
check("PROJECTS_SCHEMA", PROJECTS_SCHEMA)
check("BACKGROUND_SCHEMA", BACKGROUND_SCHEMA)
check("PROJECT_NAME_TO_LATEX", PROJECT_NAME_TO_LATEX)

print(SEP)
print("ALL PROMPTS LOADED SUCCESSFULLY")
print(SEP)
print("")
