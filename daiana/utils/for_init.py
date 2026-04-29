"""Compatibility shim — use daiana.config.settings and daiana.infra.llm_client instead."""
from daiana.config.settings import load_settings, mask_secret as _mask_secret
from daiana.infra.llm_client import build_client as build_llm_client
from daiana.services.init_service import get_local_job_hunt, ensure_env_file


def _resolve_job_hunt_dir():
    return load_settings().job_hunt_dir


def _load_job_hunt_env():
    s = load_settings()
    return s.env_path


def get_provider() -> str:
    return load_settings().provider


def get_default_model() -> str:
    return load_settings().model


__all__ = [
    "_mask_secret",
    "_resolve_job_hunt_dir",
    "_load_job_hunt_env",
    "get_provider",
    "get_default_model",
    "build_llm_client",
    "inspect_loaded_environment",
    "get_local_job_hunt",
]
