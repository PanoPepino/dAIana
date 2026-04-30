"""Compatibility shim — LaTeX helpers now live in daiana.infra.latex_repository."""
from daiana.infra.latex_repository import (
    check_pdflatex,
    detect_project_root,
    build_texinputs,
    read_log,
    extract_errors,
    get_mode_config,
    ask_for_missing as _ask_for_missing,
    resolve_mode as _resolve_mode,
    latex_escape,
    escape_bare_ampersands,
)

__all__ = [
    "check_pdflatex",
    "detect_project_root",
    "build_texinputs",
    "read_log",
    "extract_errors",
    "get_mode_config",
    "_ask_for_missing",
    "_resolve_mode",
    "latex_escape",
    "escape_bare_ampersands",
]
