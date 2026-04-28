"""Compatibility shim — hunt helpers now live in daiana.services.hunt_service and daiana.infra.filesystem."""
from daiana.services.hunt_service import _validate_hunt_mode
from daiana.infra.filesystem import open_with_default_app

__all__ = ["_validate_hunt_mode", "open_with_default_app"]
