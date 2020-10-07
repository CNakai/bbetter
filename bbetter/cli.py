import click
import bbetter.submission


@click.group()
def cli():
    pass


for command in bbetter.submission.command_group:
    cli.add_command(command)
