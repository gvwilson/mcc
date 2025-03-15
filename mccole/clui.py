"""Command-line interface for McCole."""

import click

from .build import do_build
from .check import do_check


@click.group()
def cli():
    """McCole static site generator."""
    pass


@cli.command()
@click.option("--config", type=click.Path(exists=True), help="Path to config file")
@click.option("--verbose", is_flag=True, help="Enable verbose output")
@click.option("--src", type=click.Path(), help="Source directory path")
@click.option("--dst", type=click.Path(), help="Destination directory path")
def build(config, verbose, src, dst):
    """Build the site."""
    do_build(config, verbose, src, dst)


@cli.command()
@click.option("--config", type=click.Path(exists=True), help="Path to config file")
@click.option("--verbose", is_flag=True, help="Enable verbose output")
@click.option("--src", type=click.Path(), help="Source directory path")
@click.option("--dst", type=click.Path(), help="Destination directory path")
def check(config, verbose, src, dst):
    """Check the site for errors."""
    do_check(config, verbose, src, dst)


@cli.command()
def help():
    """Show help information."""
    click.echo("Showing help information")


def main():
    """Run the command-line interface."""
    cli()


if __name__ == "__main__":
    main()
