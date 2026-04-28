"""Save service — replaces core/saver.py."""
from pathlib import Path

from daiana.infra.csv_repository import save_job, csv_path_for


def save_job_in_csv(
    career: str,
    job_position: str,
    company_name: str,
    location: str,
    job_link: str,
) -> Path:
    return save_job(
        career=career,
        job_position=job_position,
        company_name=company_name,
        location=location,
        job_link=job_link,
    )
