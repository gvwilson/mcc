"""Command-line interface for McCole."""

from pathlib import Path
import tomli
import click

from . import util


def read_config(config_file):
    """Read configuration from TOML file."""
    if not config_file.exists():
        raise click.FileError(str(config_file), hint="File not found")
    
    with config_file.open("rb") as f:
        toml_dict = tomli.load(f)
    
    return toml_dict.get("tool", {}).get("mccole", {})


@click.group()
def cli():
    """McCole static site generator."""
    pass


@cli.command()
@click.option("--config", type=click.Path(exists=True), help="Path to config file")
@click.option("--verbose", is_flag=True, help="Enable verbose output")
def build(config, verbose):
    """Build the site."""
    config_file = Path(config) if config else util.DEFAULT_CONFIG_PATH
    config_dict = read_config(config_file)
    
    click.echo(f"Building site (verbose={verbose})")
    click.echo(f"Using config from {config_file}")
    click.echo(f"Config: {config_dict}")


@cli.command()
@click.option("--config", type=click.Path(exists=True), help="Path to config file")
@click.option("--verbose", is_flag=True, help="Enable verbose output")
def check(config, verbose):
    """Check the site for errors."""
    config_file = Path(config) if config else util.DEFAULT_CONFIG_PATH
    config_dict = read_config(config_file)
    
    click.echo(f"Checking site (verbose={verbose})")
    click.echo(f"Using config from {config_file}")
    click.echo(f"Config: {config_dict}")


@cli.command()
def help():
    """Show help information."""
    click.echo("Showing help information")


def main():
    """Run the command-line interface."""
    cli()


if __name__ == "__main__":
    main()
