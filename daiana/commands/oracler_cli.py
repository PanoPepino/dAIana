from daiana.core.oracler import *
from daiana.utils.styles import DaianaCommand, command_banner, COMMAND_COLORS


def register_oracle_command(cli: click.Group) -> None:
    @cli.command("oracle", cls=DaianaCommand, help="Ask AI to tune CV & letter for a position.")
    def consult_oracle():
        """
        Provide a url with job description. Extract your best suited skills, projects and career path for it.
        """

        # Banner
        command_banner(
            "dAIana oracle: Ask the Oracle best weapons for a job  ",
            COMMAND_COLORS['oracle']
        )

        click.echo()
