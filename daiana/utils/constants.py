"""
Allowed fields or statuses that can be modified.
"""


import re

from pathlib import Path


ALLOW_STATUS = [
    "applied",
    "contacted",
    "int_1",
    "int_2",
    "offered",
    "rejected"
]


# Fields to be filled in dictionary when saving/compiling/updating
FIELDNAMES = [
    'job_position',
    'company_name',
    'location',
    'history',
    'job_link'
]

# The bunch of fields not necessary to edit
NON_EDITABLE = {
    "reasons",
    "challenge_area",
    "business_domain",
    "reason_selected_1",
    "reason_selected_2",
    "reason_selected_3",
    "_core_strength_1",
    "_core_strength_2",
    "_core_strength_3",
    "_core_strength_4",
    "_core_strength_5",
}


EDITABLE_FIELDS = [field for field in FIELDNAMES if field != "history"]


MODE_CONFIG = {
    "cv": {
        "template": Path("cv_and_letter/template_cv.tex"),
        "addon_name": "cv",
        "required_fields": [
            "career",
            "job_position",
            "company_name",
            "location",
            "job_link",
        ],
    },
    "cl": {
        "template": Path("cv_and_letter/template_cl.tex"),
        "addon_name": "cl",
        "required_fields": [
            "career",
            "job_position",
            "company_name",
            "location",
            "job_link",
            "your_background",
            "company_challenge",
        ],
    },
}


# ── Oracle: validation ────────────────────────────────────────────────────────
REQUIRED_JOB_FIELDS = ("job_position",
                       "company_name",
                       "career",
                       "location",
                       "job_link")


REQUIRED_SENTENCE_FIELDS = (
    "company_name",
    "career",
    "challenge_area",
    "business_domain",
    "sentence_first_paragraph",
)

# ── Scraper: CSS selectors (ordered, most-specific first) ─────────────────────
SCRAPE_SELECTORS = [
    {"class": "jobDescriptionContent"},   # Workday
    {"class": "description-text"},        # Workday alt
    {"class": "description__text"},       # LinkedIn
    {"id": "content"},                    # Greenhouse
    {"class": "posting-content"},         # Lever
    {"class": "job-description"},         # TeamTailor (SE/EU boards)
    {"id": "jobDescriptionText"},         # Indeed
    {"class": "job-body"},
    {"class": "job_description"},
    {"class": "vacancy-description"},
    {"role": "main"},
]

# ── Scraper: noise filter ─────────────────────────────────────────────────────
NOISE_PATTERNS = re.compile(
    r"(cookie|gdpr|privacy policy|accept all|©|\bjavascript\b)",
    re.IGNORECASE,
)

# ── Scraper: token cap ────────────────────────────────────────────────────────
SCRAPE_CHAR_LIMIT = 10_000
MIN_WORD_COUNT = 200


# ── Supported models for API services ──────────────────────────────────────────


SUPPORTED_MODELS = {
    "perplexity": {
        "sonar",
        "sonar-pro",
        "sonar-max"
    },
    "openai": {
        "gpt-4o-mini",
        "gpt-4o",
    },
}


HIDDEN_FROM_EDITOR = frozenset({
    "selected_skills_latex",
    "_skill_cat_1", "_skill_cat_2", "_skill_cat_3", "_skill_cat_4",
    "_skill_items_1", "_skill_items_2", "_skill_items_3", "_skill_items_4",
    "cv_heading_sentence",
})
