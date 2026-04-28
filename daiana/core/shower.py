"""Compatibility shim — use daiana.services.show_service instead."""
from daiana.services.show_service import get_last_jobs

__all__ = ["get_last_jobs"]
