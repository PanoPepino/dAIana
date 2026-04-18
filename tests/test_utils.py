from daiana.utils.for_csv import rewrite_filename, get_current_status
from daiana.utils.constants import ALLOW_STATUS, FIELDNAMES
from daiana.utils.ui import STATUS_COLORS
import json

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


def test_get_current_status_empty():
    result = get_current_status("{}")
    assert result == ""

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
