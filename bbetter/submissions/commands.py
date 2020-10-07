import click
from .unpack import unpack


@click.group()
def submissions():
    """Commands for manipulating student submissions"""
    pass


submissions.add_command(unpack)
group = [submissions]
