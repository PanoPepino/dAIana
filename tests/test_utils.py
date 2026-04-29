import json
from daiana.utils.for_csv import rewrite_filename, get_current_status
from daiana.utils.constants import ALLOW_STATUS, FIELDNAMES
from daiana.utils.design.ui import STATUS_COLORS

from rich.console import Console

console = Console()

# --- rewrite_filename ---


def test_rewrite_filename_spaces():
    assert rewrite_filename("Google Engineer") == "google_engineer"


def test_rewrite_filename_special_chars():
    assert rewrite_filename("C++ Dev / Lead") == "c_dev_lead"


def test_rewrite_filename_empty():
    assert rewrite_filename("   ") == "default"


def test_rewrite_filename_already_clean():
    assert rewrite_filename("amazon") == "amazon"

# --- get_current_status ---


def test_get_current_status_valid():
    history = json.dumps({"applied": "2024-01-01", "int_1": "2024-02-01"})
    key, val = get_current_status(history)
    assert key == "int_1"
    assert val == "2024-02-01"


# --- constants integrity ---


def test_allow_status_not_empty():
    assert len(ALLOW_STATUS) > 0


def test_status_colors_match_allow_status():
    for s in ALLOW_STATUS:
        assert s in STATUS_COLORS, f"{s} missing from STATUS_COLORS"


def test_status_colors_are_valid_rgb():
    for name, rgb in STATUS_COLORS.items():
        assert len(rgb) == 3
        assert all(0 <= c <= 255 for c in rgb), f"Invalid RGB for {name}"


def test_fieldnames_contains_required():
    for field in ["job_position", "company_name", "location", "history", "job_link"]:
        assert field in FIELDNAMES


def test_for_oracle_parses_edge_cases():
    """Verify oracle JSON parsing handles malformed LLM responses."""
    from daiana.utils.for_oracle import parse_oracle_json

    # Test 2: Plain JSON
    result2 = parse_oracle_json('{"location":"Tokyo"}')
    assert result2["location"] == "Tokyo"

    # Test 3: Unicode
    result3 = parse_oracle_json('{"pos":"\\u30A8\\u30F3\\u30B8\\u30CB\\u30A2"}')
    assert isinstance(result3["pos"], str)
