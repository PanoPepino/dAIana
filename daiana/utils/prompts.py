"""Compatibility shim — prompt loading now uses daiana.infra.prompt_repository.

No module-level file I/O happens here. All values are resolved on first access
through make_prompt_repository(), which requires DAIANA_JOB_HUNT_DIR to be set.
"""
from __future__ import annotations

from daiana.infra.prompt_repository import make_prompt_repository


class _Lazy:
    """Proxy that defers to make_prompt_repository() on first attribute access."""
    _repo = None

    @classmethod
    def _get(cls, key: str):
        if cls._repo is None:
            cls._repo = make_prompt_repository()
        return _GETTERS[key](cls._repo)


_GETTERS = {
    "JOB_PROMPT": lambda r: r.text("job/job_prompt"),
    "SENTENCE_PROMPT": lambda r: r.text("sentence/sentence_prompt"),
    "PROJECTS_PROMPT": lambda r: r.text("projects/projects_prompt"),
    "BACKGROUND_PROMPT": lambda r: r.text("background/background_prompt"),
    "SENTENCE_SCHEMA": lambda r: r.as_json("sentence/sentence_schema"),
    "PROJECTS_SCHEMA": lambda r: r.as_json("projects/projects_schema"),
    "BACKGROUND_SCHEMA": lambda r: r.as_json("background/background_schema"),
    "JOB_SCHEMA": lambda r: r.job_schema(),
    "PROJECTS_PAYLOAD": lambda r: r.text("projects/projects_payload"),
    "BACKGROUND_PAYLOAD": lambda r: r.text("background/background_payload"),
    "PROJECT_NAME_TO_LATEX": lambda r: r.as_json("projects/projects_name_to_latex"),
    "CAREERS_CONFIG": lambda r: r.as_json("career/careers"),
    "CAREERS": lambda r: r.careers(),
    "BACKGROUND": lambda r: r.background_list(),
}


def __getattr__(name: str):
    if name in _GETTERS:
        return _Lazy._get(name)
    raise AttributeError(f"module 'daiana.utils.prompts' has no attribute {name!r}")
