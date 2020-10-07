import click
import bbetter.submissions.commands


@click.group()
def cli():
    pass


for command in bbetter.submissions.commands.group:
    cli.add_command(command)
