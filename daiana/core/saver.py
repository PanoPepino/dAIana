from pathlib import Path
from datetime import date
import csv
import json

from daiana.utils.for_csv import check_dir_exist, rewrite_filename


def save_job_in_csv(career: str,
                    job_position: str,
                    company_name: str,
                    location: str,
                    job_link: str) -> Path:
    """
    This function is designed to eat several input and store them as columns in a given `career`.csv.

    Args:
        career (str): The career path (i.e. the .csv document) where things will be stored. If it does not yet exist, it will be created.
        job_position (str): The title of the job position you wanna apply for.
        company_name (str): The name of the company offering the job.
        location (str): Assuming it is hybrid, the city where the company is located.
        job_link (str): The html link to the job description/application page.

    Returns:
        Path: The path where the .csv file is located after updating.
    """

    when = date.today().isoformat()
    history = {"applied": when}
    data_dir = check_dir_exist()
    rewritten = rewrite_filename(career)
    csv_path = data_dir/f"{rewritten}_jobs.csv"
    csv_path.parent.mkdir(parents=True, exist_ok=True)

    job_info = {'job_position': job_position,
                'company_name': company_name,
                'city': location,
                'history': json.dumps(history),
                'job_link': job_link}

    file_exists = csv_path.exists()

    with csv_path.open("a", newline="", encoding='utf-8') as f:
        writer = csv.DictWriter(
            f,
            fieldnames=job_info.keys()
        )
        if not file_exists:
            writer.writeheader()
        writer.writerow(job_info)

    return csv_path
