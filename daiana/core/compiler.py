"""Compatibility shim — use daiana.services.compile_service instead."""
from daiana.services.compile_service import (
    _collect_compile_data,
    build_replacements,
    render_template,
    compile_tex,
    render_and_compile,
    compile_with_data,
)

__all__ = [
    "_collect_compile_data",
    "build_replacements",
    "render_template",
    "compile_tex",
    "render_and_compile",
    "compile_with_data",
]
