import click
from pathlib import Path

from daiana.core.compiler import _resolve_mode, compile_with_data
from daiana.core.saver import *
from daiana.utils.styles import DaianaCommand, command_banner, COMMAND_COLORS


def register_compile_command(cli: click.Group) -> None:
    @cli.command("compile", cls=DaianaCommand, help="Compile CV or cover letter for a job position. Optional saving in .csv database")
    @click.option("--cv", "mode", flag_value="cv", help="CV mode")
    @click.option("--cl", "mode", flag_value="cl", help="Cover letter mode")
    @click.option("--username", "-un", default="user_name", help="Your name to appear in PDF name")
    @click.option("--verbose", is_flag=True, help="Latex compilation will provide information")
    def compile_from_template(mode: str | None, username: str, verbose: bool) -> None:
        command_banner(
            "dAIana compiler: CV & cover letter sharpening tool",
            COMMAND_COLORS["compile"],
        )

        mode = _resolve_mode(mode)

        try:
            replacements, template = compile_with_data(
                mode=mode,
                username=username,
                verbose=verbose,
                seed_data=None,
            )
        except Exception as exc:
            raise click.ClickException(f"Compilation failed: {exc}") from exc

        click.echo()
        click.echo(
            click.style("Compiled! ", fg=COMMAND_COLORS["compile"], bold=True)
            + click.style("see the PDF generated from: ", fg="white")
            + click.style(f"{template.name}")
        )
        click.echo()

        if click.confirm(
            click.style("Would you like to save this job info in CSV?", fg=COMMAND_COLORS["save"]),
            default=False,
        ):
            click.echo(click.style("Storing job info in CSV...", fg=COMMAND_COLORS["save"]))
            csv_path = save_job_in_csv(
                career=replacements["career"],
                job_position=replacements["job_position"],
                company_name=replacements["company_name"],
                location=replacements["location"],
                job_link=replacements["job_link"],
            )
            click.echo(
                click.style("Saved ", fg=COMMAND_COLORS["save"], bold=True)
                + click.style("Job info stored at: ", fg="white")
                + click.style(f"{csv_path}_jobs.csv")
            )
            click.echo()
        else:
            click.echo(click.style("Job info not saved in CSV.", fg=COMMAND_COLORS["save"]))
            click.echo()
