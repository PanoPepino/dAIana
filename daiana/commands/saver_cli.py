import click

from daiana.core.saver import save_job_in_csv


def register_save_command(cli: click.Group) -> None:
    @cli.command("save")
    @click.option('--career', '-cp', required=True, help='Career path (e.g., "software")')
    def save_job(career: str) -> None:
        """
        This function will call save_job_in_csv function in daiana.saver. It will ask you for some  inputs and save them in .csv with the choosen career.
        """

        click.echo()
        click.echo(click.style("┌──────────────────────────────────────────────────────────┐",  fg="bright_cyan"))
        click.echo(click.style("│      dAIana saver: Store your job information in CSV     │",  fg="bright_cyan", bold=True))
        click.echo(click.style("└──────────────────────────────────────────────────────────┘",  fg="bright_cyan"))
        click.echo()
        click.echo(click.style("--- Store your new hunting trophies ---", fg="cyan"))
        click.echo()

        click.echo(click.style("Fill in the fields below:", fg="cyan"))
        click.echo()
        # career = click.prompt(click.style("1) Career path", fg="white", bold=True))
        job_position = click.prompt(click.style("1) Job position", fg="white", bold=True))
        company_name = click.prompt(click.style("2) Company name", fg="white", bold=True))
        location = click.prompt(click.style("3) Location", fg="white", bold=True), default='',  show_default=False)
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
            click.style("Saved ", fg="cyan", bold=True)
            + click.style("Job info stored at: ", fg="white")
            + click.style(f"{csv_path}_jobs.csv")
        )
        click.echo()
