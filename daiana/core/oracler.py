"""Compatibility shim — use daiana.services.oracle_service instead."""
from daiana.services.oracle_service import (
    run_oracle_pipeline,
    run_oracle_flow,
    edit_oracle_dict,
    parse_oracle_json,
    unicode_to_utf8,
    clean_city_location,
    normalize_project_selection,
    dict_values_to_sentence,
    _display_oracle_result,
)
from daiana.utils.design.ui import _display_oracle_result

__all__ = [
    "run_oracle_pipeline",
    "run_oracle_flow",
    "edit_oracle_dict",
    "parse_oracle_json",
    "unicode_to_utf8",
    "clean_city_location",
    "normalize_project_selection",
    "dict_values_to_sentence",
    "_display_oracle_result",
]
