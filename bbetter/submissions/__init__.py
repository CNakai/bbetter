import click
from .unpack import unpack


@click.group(name='submissions')
def __submissions():
    """Commands for manipulating student submissions"""
    pass


__submissions.add_command(unpack)
command_group = [__submissions]
