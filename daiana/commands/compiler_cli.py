import click
from daiana.utils.for_latex import render_template
from pathlib import Path
from daiana.core.compiler import compile_tex
from daiana.core.saver import save_job_in_csv
from daiana.utils.styles import *


def register_compile_command(cli: click.Group) -> None:
    @cli.command("compile", help="Compile CV or cover letter for a job position. Optional saving in .csv database")
    @click.pass_context
    @click.option("--cv", "mode", flag_value="cv", help="CV mode")
    @click.option("--cl", "mode", flag_value="cl", help="Cover letter mode")
    @click.option("--username", "-un", default="user_name", help="your name to appear in .pdf name")
    def compile_from_template(ctx: click.Context, mode: str, username):
        """
        Render a .tex template (template_something.tex), then compile it.
        """

        # Banner
        command_banner(
            "dAIana compiler: CV & cover letter sharpening tool",
            COMMAND_COLORS['compile']
        )

        click.echo(click.style("Fill in fields below:", fg=COMMAND_COLORS['compile']))
        click.echo()

        # Auto-select template
        if mode == "cv":
            template = Path("cv_and_letter/template_cv.tex")
            addon_name = "cv"
        elif mode == "cl":
            template = Path("cv_and_letter/template_cl.tex")
            addon_name = "cl"
        else:
            raise click.UsageError("Use --cv, --cl")

        career = click.prompt(click.style("1) Career", fg="white", bold=True))

        # Conditional prompts by mode
        replacements = {
            "job_position": click.prompt(click.style("2) Job Position", fg="white", bold=True)),
            "company_name": click.prompt(click.style("3) Company Name", fg="white", bold=True)),
            "location": click.prompt(click.style("4) Job Location", fg="white", bold=True)),
            "career": career,
            "job_link": click.prompt(click.style("5) Job Link", fg="white", bold=True), default='')
        }
        click.echo()

        if mode == "cv" or not mode:
            replacements.update({})  # To be modified when modular
        elif mode == "cl":
            replacements.update(
                {
                    "your_background": click.prompt(
                        click.style("Your tailored background", fg="white", bold=True)
                    ),
                    "company_challenge": click.prompt(
                        click.style("The company's challenge(s)", fg="white", bold=True)
                    ),
                    "cp_latex": "\\body" + career,
                }
            )

        # Render & compile
        to_feed = render_template(
            template,
            replacements,
            stem_replacement=f"{username}_{addon_name}",
        )
        compile_tex(to_feed)

        click.echo()
        click.echo(
            click.style("Compiled! ", fg=COMMAND_COLORS['compile'], bold=True)
            + click.style("see the PDF generated from: ", fg="white")
            + click.style(f"{template.name}")
        )
        click.echo()

        # Ask yes/no after compile
        if click.confirm(
            click.style("Would you like to save this job info in CSV?", fg="cyan"),
            default=False,
        ):
            click.echo(
                click.style("Storing job info in CSV...", fg="cyan")
            )
            csv_path = save_job_in_csv(
                career=replacements["career"],
                job_position=replacements["job_position"],
                company_name=replacements["company_name"],
                location=replacements["location"],
                job_link=replacements['job_link'],
            )
            click.echo(
                click.style("Saved ", fg="cyan", bold=True)
                + click.style("Job info stored at: ", fg="white")
                + click.style(f"{csv_path}_jobs.csv")
            )
        else:
            click.echo(click.style("Job info not saved in CSV.", fg="cyan"))
