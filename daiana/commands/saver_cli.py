import click

from daiana.core.saver import save_job_in_csv
from daiana.utils.constants import COMMAND_COLORS
from daiana.utils.styles import DaianaCommand, command_banner


def register_save_command(cli: click.Group) -> None:
    @cli.command("save", cls=DaianaCommand, help="Save a new job you have applied to in a .csv file.")
    @click.option('--career', '-cp', required=True, help='Career path (e.g., "software")')
    def save_job(career: str) -> None:
        """
        Save the jobs you have applied to in a .csv file for easier tracking.
        """

        command_banner(
            "dAIana saver: Store your job hunt trophies",
            COMMAND_COLORS['save']
        )

        click.echo(click.style("Fill in the fields below:", fg=COMMAND_COLORS['save']))
        click.echo()

        job_position = click.prompt(click.style("1) Job position", fg="white", bold=True))
        company_name = click.prompt(click.style("2) Company name", fg="white", bold=True))
        location = click.prompt(click.style("3) Location", fg="white", bold=True), default='', show_default=False)
        job_link = click.prompt(
            click.style("4) Link to job description ", fg="white", bold=True) +
            click.style('(press ENTER if none)', fg='white'),
            default='',
            show_default=False
        )
        click.echo()

        csv_path = save_job_in_csv(
            career=career,
            job_position=job_position,
            company_name=company_name,
            location=location,
            job_link=job_link,
        )

        click.echo(
            click.style("Saved ", fg=COMMAND_COLORS['save'], bold=True)
            + click.style("Job info stored at: ", fg="white")
            + click.style(f"{csv_path}_jobs.csv")
        )
        click.echo()
