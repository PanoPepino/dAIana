"""Compatibility shim — use daiana.services.hunt_service instead."""
from daiana.services.hunt_service import run_hunt_flow

__all__ = ["run_hunt_flow"]
