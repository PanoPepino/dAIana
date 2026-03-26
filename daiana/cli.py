#!/usr/bin/env python
import click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich import box

from daiana.commands.compiler_cli import register_compile_command
from daiana.commands.saver_cli import register_save_command
from daiana.commands.shower_cli import register_show_command
from daiana.commands.updater_cli import register_update_command


console = Console()


@click.group()
def cli():
    """🏹 dAIana - Job Hunting LaTeX Automation enhanced with AI"""
    pass


def print_banner():
    """
    Print the fancy aligned banner
    """

    banner_text = Text.assemble(
        ("🎯 SAVE:     Save job targets to career CSV with auto-timestamps", "bold cyan"),
        "\n",
        ("📊 SHOW:     Inspect recent jobs in fancy colored table", "bold magenta"),
        "\n",
        ("🔄 UPDATE:   Modify job status/history", "bold yellow"),
        "\n",
        ("📄 COMPILE:  LaTeX CV automation", "bold green"),
    )

    panel = Panel(
        banner_text,
        title="🏹  dAIana 🎯",
        subtitle="Job Hunting LaTeX Automation enhanced with AI",
        width=72,
        box=box.HEAVY,
        title_align="center",
        subtitle_align="center",
    )
    console.print(panel)


@cli.command()
def help():
    """Show the fancy help banner"""
    print_banner()


for register in [
    register_compile_command,
    register_save_command,
    register_show_command,
    register_update_command,
]:
    register(cli)


if __name__ == "__main__":
    print_banner()
    cli()
