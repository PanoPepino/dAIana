from daiana.core.oracler import *
from daiana.utils.styles import *


def register_hunt_command(cli: click.Group) -> None:
    @cli.command("hunt", help="Ask AI, choose skills, compile documents & track job.")
    def hunt_job():
        """
        TO FIX
        """

        # Banner
        command_banner(
            "dAIana hunt: Ask guidance. Choose weapons. Track. Hunt",
            COMMAND_COLORS['hunt']
        )

        # Working on it!

        # click.echo(click.style("Fill in fields below:", fg=COMMAND_COLORS['compile']))
        click.echo()
