import click
from .get import get
from .unpack import unpack


@click.group(name='submission')
def __submission():
    """Commands for manipulating student submissions"""
    pass


__submission.add_command(get)
__submission.add_command(unpack)
command_group = [__submission]
