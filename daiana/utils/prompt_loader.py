"""
Utilities for loading Markdown prompt files used by Daiana.

Expected project structure:

project_root/
├── daiana/
│   └── utils/
│       └── prompt_loader.py
├── cv_and_letter/
├── job_tracking/
└── prompts/
    ├── background/
    │   ├── background_payload.md
    │   ├── background_prompt.md
    │   └── background_schema.md
    ├── career/
    │   └── careers.md
    ├── job/
    │   ├── job_prompt.md
    │   └── job_schema.md
    ├── projects/
    │   ├── projects_name_to_latex.md
    │   ├── projects_payload.md
    │   ├── projects_prompt.md
    │   └── projects_schema.md
    └── sentence/
        ├── sentence_prompt.md
        └── sentence_schema.md
"""

from pathlib import Path
import click


class PromptLoader:
    """
    Load Markdown prompt files from the project's top-level `job_hunt/prompts/` folder.

    Paths are resolved relative to the project root, not the shell's current
    working directory, so the loader behaves consistently across scripts.
    """

    def __init__(self, prompts_dir: str = "job_hunt/prompts"):
        self._prompts_dir_name = prompts_dir

    @property
    def project_root(self) -> Path:
        """
        Resolve the project root from this file's location.

        prompt_loader.py lives in:
            daiana/utils/prompt_loader.py

        so the project root is two levels above this file's parent:
            project_root/
                daiana/
                    utils/
                        prompt_loader.py
        """
        return Path(__file__).resolve().parents[2]

    @property
    def prompts_dir(self) -> Path:
        """Return the absolute path to the prompts directory."""
        return self.project_root / self._prompts_dir_name

    def load(self, name: str, fallback: str | None = None) -> str:
        """
        Load one prompt file by relative path inside `prompts/`.

        Examples:
            loader.load("background/background_payload")
            loader.load("job/job_prompt")
            loader.load("projects/projects_schema")
        """
        path = self.prompts_dir / f"{name}.md"

        if path.exists() and path.is_file():
            return path.read_text(encoding="utf-8").strip()

        if fallback is not None:
            return fallback.strip()

        raise click.ClickException(
            f"Prompt file not found: {path}\n"
            f"Resolved project root: {self.project_root}\n"
            f"Resolved prompts dir: {self.prompts_dir}\n"
            f"Make sure the file exists and matches the expected nested structure."
        )

    def load_all(self) -> dict[str, str]:
        """Load all markdown prompt files under `prompts/` recursively."""
        if not self.prompts_dir.exists():
            raise click.ClickException(
                f"Prompts directory not found: {self.prompts_dir}\n"
                f"Resolved project root: {self.project_root}"
            )

        prompt_files = sorted(
            path for path in self.prompts_dir.rglob("*.md") if path.is_file()
        )

        if not prompt_files:
            raise click.ClickException(
                f"No markdown prompt files found under: {self.prompts_dir}"
            )

        return {
            str(path.relative_to(self.prompts_dir).with_suffix("")): path.read_text(
                encoding="utf-8"
            ).strip()
            for path in prompt_files
        }


loader = PromptLoader()
