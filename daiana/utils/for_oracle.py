"""Compatibility shim — oracle helpers now live in daiana.services.oracle_service."""
from daiana.services.oracle_service import (
    unicode_to_utf8,
    clean_city_location,
    edit_oracle_dict,
    parse_oracle_json,
    normalize_project_selection,
    dict_values_to_sentence,
)
from daiana.infra.scraper import scrape_job_text
from daiana.domain.validation import (
    validate_job_data as _validate_job_data,
    validate_sentence_data as _validate_sentence_data,
    validate_project_data as _validate_project_data,
    validate_background_data as _validate_background_data,
)

__all__ = [
    "unicode_to_utf8",
    "clean_city_location",
    "edit_oracle_dict",
    "parse_oracle_json",
    "normalize_project_selection",
    "dict_values_to_sentence",
    "scrape_job_text",
    "_validate_job_data",
    "_validate_sentence_data",
    "_validate_project_data",
    "_validate_background_data",
]
