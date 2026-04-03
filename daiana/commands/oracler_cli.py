import click
from pathlib import Path

from daiana.utils.for_oracle import edit_oracle_dict
from daiana.core.oracler import run_oracle_pipeline
from daiana.utils.styles import DaianaCommand, command_banner, COMMAND_COLORS


def register_oracle_command(cli: click.Group) -> None:
    @cli.command("oracle", cls=DaianaCommand, help="Ask AI to tune CV & letter for a position.")
    @click.option("-u", "--url", required=True, help="Job URL to scrape and parse as JSON oracle record.")
    @click.option(
        "--csv-path",
        type=click.Path(path_type=Path),
        default=Path("job_tracking"),
        show_default=True,
        help="CSV file path reserved for existing daiana logic.",
    )
    @click.option(
        "--extract",
        is_flag=True,
        help="Extract basic information from the job position.",
    )
    @click.option(
        "--tailor_cl",
        "tailor_cl",
        is_flag=True,
        help="Generate simple tailored cover-letter sentences from the job description.",
    )
    def consult_oracle(url: str, csv_path: Path, extract: bool, tailor_cl: bool) -> None:
        command_banner(
            "dAIana oracle: Ask guidance to the Oracle ",
            COMMAND_COLORS["oracle"],
        )

        if not extract and not tailor_cl:
            raise click.ClickException("Use at least one flag: --extract and/or --tailor-cl")

        try:
            if extract and tailor_cl:
                click.secho(
                    "Extracting job information and crafting tailored sentence(s) ...",
                    fg=COMMAND_COLORS["oracle"],
                )
            elif extract:
                click.secho(
                    "Extracting information of your next trophy ...",
                    fg=COMMAND_COLORS["oracle"],
                )
            else:
                click.secho(
                    "Tailoring your requested sentence(s) ...",
                    fg=COMMAND_COLORS["oracle"],
                )

            click.echo()

            result = run_oracle_pipeline(
                url=url,
                extract=extract,
                tailor_cl=tailor_cl,
            )

        except ValueError as exc:
            raise click.ClickException(str(exc)) from exc
        except Exception as exc:
            raise click.ClickException(f"Oracle failed: {exc}") from exc

        if not isinstance(result, dict):
            raise click.ClickException("Oracle pipeline did not return a dictionary.")

        if not result:
            raise click.ClickException("Oracle returned an empty result.")

        click.secho("Oracle result:", fg=COMMAND_COLORS["oracle"])
        click.echo()

        for key, value in result.items():
            click.echo(f"{key:17}: {value}")

        click.echo()

        if click.confirm(
            click.style("Would you like to modify this information?", fg=COMMAND_COLORS["oracle"]),
            default=False,
        ):
            result = edit_oracle_dict(result)

            click.echo()
            click.secho("The new fields are:", fg=COMMAND_COLORS["oracle"])

            for key, value in result.items():
                click.echo(f"{key:17}: {value}")

            click.echo()
