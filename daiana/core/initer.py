"""Compatibility shim — use daiana.services.init_service instead."""
from daiana.services.init_service import (
    get_local_job_hunt,
    ensure_env_file,
    copy_directory_func,
    set_env_func,
)

__all__ = [
    "get_local_job_hunt",
    "ensure_env_file",
    "copy_directory_func",
    "set_env_func",
]
