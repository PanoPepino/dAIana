import click
from daiana.core.oracler import *
from daiana.utils.styles import DaianaCommand, command_banner, COMMAND_COLORS


def register_hunt_command(cli: click.Group) -> None:
    @cli.command("hunt", cls=DaianaCommand, help="Ask AI, choose skills, compile documents & track job.")
    def hunt_job():
        """
        TO FIX
        """

        # Banner
        command_banner(
            "dAIana hunt: Ask guidance. Choose weapons. Track. Hunt",
            COMMAND_COLORS['hunt']
        )

        click.echo()
