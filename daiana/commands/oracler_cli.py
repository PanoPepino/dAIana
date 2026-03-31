import click
import os

from openai import OpenAI
from pathlib import Path
from dotenv import load_dotenv
from daiana.utils.for_oracle import scrape_job_text, edit_oracle_dict
from daiana.utils.for_csv import filter_job_dict
from daiana.core.saver import *
from daiana.core.oracler import *
from daiana.utils.styles import DaianaCommand, command_banner, COMMAND_COLORS


def register_oracle_command(cli: click.Group) -> None:
    @cli.command("oracle", cls=DaianaCommand, help="Ask AI to tune CV & letter for a position.")
    @click.option("-u", "--url", help="Job URL to scrape and parse as JSON oracle record.", required=True)
    @click.option(
        "--csv-path",
        type=click.Path(path_type=Path),
        default=Path("job_tracking"),
        show_default=True,
        help="CSV file to append job record (for existing daiana logic).",
    )
    def consult_oracle(url: str, csv_path: Path):
        """
        Provide a url with job description. Extract your best suited skills, projects and career path for it.
        """

        # Banner
        command_banner(
            "dAIana oracle: Ask the Oracle best weapons for a job  ",
            COMMAND_COLORS['oracle']
        )

        load_dotenv()  # Load the .env with the key (secret) <- Requires to be setted as .env by user
        client = OpenAI(api_key=os.getenv("PERPLEXITY_API_KEY"),
                        base_url="https://api.perplexity.ai")

        click.secho("Extracting information of your next trophy ...", fg=COMMAND_COLORS['oracle'])
        click.echo()
        job_text = scrape_job_text(url)

        click.secho("Asking the Oracle best suitable path ...", fg=COMMAND_COLORS['oracle'])
        click.echo()
        job_data = extract_job_via_oracle(job_text, url, client)
        click.secho("These is the relevant information to be used ...", fg=COMMAND_COLORS['oracle'])
        click.echo()
        for k, v in job_data.items():
            click.echo(f"{k:14}: {v}")

        click.echo()
        sentence = write_sentence_via_oracle(job_text, url, client)
        click.secho("These are BLABLA ...", fg=COMMAND_COLORS['oracle'])
        click.echo()
        for k, v in sentence.items():
            click.echo(f"{k:14}: {v}")

        click.echo()

        if click.confirm(
            click.style("Would you like to modify this information?", fg=COMMAND_COLORS['oracle']),
            default=False,
        ):

            job_data = edit_oracle_dict(job_data)
            click.echo()
            click.echo("The new fields are:")
            for k, v in job_data.items():
                click.echo(f"{k:14}: {v}")
            click.echo()

        else:
            pass

        # THIS PIECE SHOULD GO INTO THE FINAL HUNT.
        click.secho("Saving JSON and CSV...", fg=COMMAND_COLORS['save'])
        click.echo()
        save_job_in_csv(
            career=job_data["career"],
            **filter_job_dict(job_data))
