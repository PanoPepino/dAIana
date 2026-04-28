"""Compatibility shim — use daiana.services.save_service instead."""
from daiana.services.save_service import save_job_in_csv
from daiana.infra.csv_repository import csv_path_for

__all__ = ["save_job_in_csv", "csv_path_for"]
