"""Main CLI entry point for Daiana"""
import click

from daiana.commands.saver_cli import register_save_command
from daiana.commands.shower_cli import register_show_command
from daiana.commands.updater_cli import register_update_command
from daiana.commands.compiler_cli import register_compile_command


@click.group()
@click.version_option("0.1.0")
def cli():
    """
╔══════════════════════════════════════════════════════════════════════╗
║                           🏹  dAIana 🎯                              ║
║                                                                      ║
║            Job Hunting LaTeX Automation enhanced with AI             ║
╚══════════════════════════════════════════════════════════════════════╝

🎯 SAVE:     Save job targets to career CSV with auto-timestamps
📊 SHOW:     Inspect recent jobs in fancy colored table
🔄 UPDATE:   Modify job status/history
📄 COMPILE:  LaTeX CV automation

💡 daiana <command> --help
    """
    pass


register_save_command(cli)
register_show_command(cli)
register_update_command(cli)
register_compile_command(cli)

if __name__ == '__main__':
    cli()
