import click
from pathlib import Path

from daiana.utils.for_oracle import edit_oracle_dict
from daiana.core.oracler import run_oracle_pipeline
from daiana.utils.styles import DaianaCommand, command_banner, COMMAND_COLORS


def register_oracle_command(cli: click.Group) -> None:
    @cli.command("oracle", cls=DaianaCommand, help="Ask AI to tune CV & letter for a position.")
    @click.option("-u", "--url", required=True, help="Job URL to scrape and parse.")
    @click.option(
        "--csv-path",
        type=click.Path(path_type=Path),
        default=Path("job_tracking"),
        show_default=True,
        help="CSV file path reserved for existing daiana logic.",
    )
    @click.option("--extract", is_flag=True, help="Extract structured job metadata (position, company, career, location).")
    @click.option("--tailor_sentence", is_flag=True, help="Generate tailored background + challenge slots for the cover letter.")
    @click.option("--select_projects", is_flag=True, help="Select the 3 most relevant CV projects for this job posting.")
    @click.option("--select_background", is_flag=True, help="Select the 3 most relevant background skills for the cover letter.")
    def consult_oracle(
        url: str,
        csv_path: Path,
        extract: bool,
        tailor_sentence: bool,
        select_projects: bool,
        select_background: bool
    ) -> None:

        command_banner("dAIana oracle: Ask guidance to the Oracle   ", COMMAND_COLORS["oracle"])

        if not any([extract, tailor_sentence, select_projects, select_background]):
            raise click.ClickException(
                "Use at least one flag: --extract, --tailor_sentence, --select_projects, --select_background"
            )

        # ── Status message ────────────────────────────────────────────────────
        active = []
        if extract:
            active.append("extracting job metadata")
        if tailor_sentence:
            active.append("tailoring cover letter slots")
        if select_projects:
            active.append("selecting relevant projects")
        if select_background:
            active.append("selecting relevant background skills")

        click.secho(f"Oracle is: {', '.join(active)} ...", fg=COMMAND_COLORS["oracle"])
        click.echo()

        # ── Run pipeline ──────────────────────────────────────────────────────
        try:
            result = run_oracle_pipeline(
                url=url,
                extract=extract,
                tailor_sentence=tailor_sentence,
                select_projects=select_projects,
                select_background=select_background
            )
        except ValueError as exc:
            raise click.ClickException(str(exc)) from exc
        except Exception as exc:
            raise click.ClickException(f"Oracle failed: {exc}") from exc

        if not isinstance(result, dict) or not result:
            raise click.ClickException("Oracle returned an empty or invalid result.")

        print(result)

        # ── Display result ────────────────────────────────────────────────────
        click.echo()
        _display_oracle_result(result)

        # ── Optional edit (skipped for project selection — not user-editable) ─
        NON_EDITABLE = ['reasons', 'challenge_area', 'business_domain',
                        'reason_name_1', 'reason_name_2', 'reason_name_3']
        editable = {k: v for k, v in result.items()
                    if k not in NON_EDITABLE}

        if editable and click.confirm(
            click.style("Would you like to modify this information?", fg=COMMAND_COLORS["oracle"]),
            default=False,
        ):
            updated = edit_oracle_dict(editable)
            result.update(updated)

            click.echo()
            click.secho("Updated fields:", fg=COMMAND_COLORS["update"])
            click.echo()
            for key, value in editable.items():
                click.echo(f"{key:17}: {value}")
            click.echo()


def _echo_field(label: str, value: str) -> None:
    click.echo(f"{label:17}: {value}")


def _display_oracle_result(result: dict) -> None:
    click.secho("Result:", fg=COMMAND_COLORS["oracle"])
    click.echo()

    # ── Pack 1: Extracted data ───────────────────────────────────────
    click.secho("Extracted data", fg=COMMAND_COLORS["oracle"], bold=True)
    click.echo()
    _echo_field("job_position", result.get("job_position", ""))
    _echo_field("company_name", result.get("company_name", ""))
    _echo_field("career", result.get("career", ""))
    _echo_field("location", result.get("location", ""))
    _echo_field("job_link", result.get("job_link", ""))
    click.echo()

    # ── Pack 2: Background and Tailored sentence ────────────────────────────────────
    click.secho("Background skills and tailored sentence", fg=COMMAND_COLORS["oracle"], bold=True)
    click.echo()
    _echo_field(
        "sentence_first_paragraph",
        result.get("sentence_first_paragraph", ""),
    )
    _echo_field("your_background", result.get("your_background", ""))
    click.echo()

    # ── Pack 3: Selected projects ────────────────────────────────────
    click.secho("Selected projects", fg=COMMAND_COLORS["oracle"], bold=True)
    click.echo()
    _echo_field("project_one", result.get("project_one", ""))
    _echo_field("project_two", result.get("project_two", ""))
    _echo_field("project_three", result.get("project_three", ""))
    click.echo()

    # ── Extra material ───────────────────────────────────────────────
    click.secho("Extra material (will not be passed to LaTeX)", fg=COMMAND_COLORS["oracle"], bold=True)
    click.echo()
    _echo_field("challenge_area", result.get("challenge_area", ""))
    _echo_field("business_domain", result.get("business_domain", ""))
    click.echo()

    click.echo("Reasons for choosing those projects:")
    for i, proj_key in enumerate(["project_one", "project_two", "project_three"], 1):
        proj_name = result.get(proj_key, "")
        reason_key = f"reason_name_{i}"
        reason = result.get(reason_key, "-")
        click.echo(f"  {proj_name:15}: {reason}")
    click.echo()
