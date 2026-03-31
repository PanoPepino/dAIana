# To check and test basic latex commands of the project

from daiana.utils.for_latex import render_template
from pathlib import Path
import pytest


def test_render_template_creates_file(tmp_path):
    # Create a minimal fake .tex template
    template = tmp_path / "cv_template.tex"
    template.write_text(r"\newcommand{\company_name}{PLACEHOLDER}", encoding="utf-8")

    replacements = {"company_name": "Google"}
    result_path = render_template(template, replacements)

    assert result_path.exists()
    content = result_path.read_text(encoding="utf-8")
    assert "Google" in content

    # cleanup
    result_path.unlink()
