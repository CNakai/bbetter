import click
import bbetter.submissions


@click.group()
def cli():
    pass


for command in bbetter.submissions.command_group:
    cli.add_command(command)
