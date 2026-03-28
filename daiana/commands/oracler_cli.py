from daiana.core.oracler import *
from daiana.utils.styles import *


def register_oracle_command(cli: click.Group) -> None:
    @cli.command("oracle", help="Ask AI to tune CV & letter for a position.")
    def consult_oracle():
        """
        Provide a url with job description. Extract your best suited skills, projects and career path for it.
        """

        # Banner
        command_banner(
            "dAIana oracle: Ask the Oracle best weapons for a job  ",
            COMMAND_COLORS['oracle']
        )

        # Working on it!

        # click.echo(click.style("Fill in fields below:", fg=COMMAND_COLORS['compile']))
        click.echo()
