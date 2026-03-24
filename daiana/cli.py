"""Main CLI entry point for Daiana"""

import click
from daiana.saver import *
from daiana.shower import *
from daiana.commands_cli.saver_cli import register_save_command
from daiana.commands_cli.shower_cli import register_show_command
from daiana.commands_cli.updater_cli import register_update_command


@click.group()
@click.version_option()
def cli():  # This is what appears when you call the package --help
    """
    ===== Daiana =====

    A tool that aims to be LaTeX CV/Cover Letter Automation for Job Hunting.

    It will help you manage and compile LaTeX documents for your job applications in a straight forward way just using your terminal and some inputs.
    """
    pass


register_save_command(cli)
register_show_command(cli)
register_update_command(cli)


if __name__ == '__main__':
    cli()
