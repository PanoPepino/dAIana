"""Domain dataclasses — the shapes that flow between services."""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class JobInfo:
    career: str
    job_position: str
    company_name: str
    location: str
    job_link: str


@dataclass
class ProjectSelection:
    project_one: str = ""
    project_two: str = ""
    project_three: str = ""
    reason_selected_1: str = ""
    reason_selected_2: str = ""
    reason_selected_3: str = ""


@dataclass
class CoverLetterData:
    your_background: str = ""
    sentence_first_paragraph: str = ""
    challenge_area: str = ""
    business_domain: str = ""
    company_name: str = ""
    career: str = ""


@dataclass
class CompileRequest:
    mode: str  # 'cv' or 'cl'
    username: str
    verbose: bool = False
    seed_data: dict = field(default_factory=dict)
