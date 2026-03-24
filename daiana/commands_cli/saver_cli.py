import click
from daiana.saver import save_job_in_csv
from datetime import date


def register_save_command(cli: click.Group) -> None:
    @cli.command("save")
    def save_job() -> None:
        """
        This function will call save_job_in_csv function in daiana.saver. It will ask you for some  inputs and save them in .csv with the choosen career_path.
        """

        click.echo()
        click.echo(click.style("┌──────────────────────────────────────────────────────────┐",  fg="bright_cyan"))
        click.echo(click.style("│      dAIana saver: store your job information in CSV     │",  fg="bright_cyan", bold=True))
        click.echo(click.style("└──────────────────────────────────────────────────────────┘",  fg="bright_cyan"))
        click.echo()

        click.echo(click.style("Fill in the fields below:", fg="cyan"))
        click.echo()
        career_path = click.prompt(click.style("1) Career path", fg="white", bold=True))
        job_position = click.prompt(click.style("2) Job position", fg="white", bold=True))
        company_name = click.prompt(click.style("3) Company name", fg="white", bold=True))
        location = click.prompt(click.style("4) Location", fg="white", bold=True), default='',  show_default=False)
        job_link = click.prompt(
            click.style("5) Link to job description ", fg="white", bold=True) +
            click.style('(press ENTER if none)', fg='white'),
            default='',
            show_default=False
        )
        click.echo()

        csv_path = save_job_in_csv(
            career_path=career_path,
            job_position=job_position,
            company_name=company_name,
            location=location,
            status='applied',
            job_link=job_link,
        )

        click.echo(
            click.style("Saved ", fg="cyan", bold=True)
            + click.style("Job info stored at: ", fg="white")
            + click.style(f"{csv_path}_jobs.csv")
        )
        click.echo()
