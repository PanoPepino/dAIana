from pathlib import Path
import os
import click


class PromptLoader:
    @property
    def job_hunt_dir(self) -> Path:
        env_dir = os.getenv("DAIANA_JOB_HUNT_DIR")
        if env_dir:
            path = Path(env_dir).expanduser().resolve()
            if path.exists():
                return path

        cwd = Path.cwd().resolve()
        if (cwd / "prompts").exists():
            return cwd

        raise click.ClickException(
            "Missing job_hunt directory. Provide --job-hunt-dir or set DAIANA_JOB_HUNT_DIR."
        )

    @property
    def prompts_dir(self) -> Path:
        path = self.job_hunt_dir / "prompts"
        if not path.exists():
            raise click.ClickException(f"Prompts directory not found: {path}")
        return path

    def load(self, name: str) -> str:
        path = self.prompts_dir / f"{name}.md"
        if not path.exists():
            raise click.ClickException(f"Prompt file not found: {path}")
        return path.read_text(encoding="utf-8")


loader = PromptLoader()
