"""Build functionality for McCole."""

from pathlib import Path
import click

from . import util


def do_build(config, verbose, src, dst):
    """Build the site."""
    config_file = Path(config) if config else util.DEFAULT_CONFIG_PATH
    config = util.read_config(config_file, verbose, src, dst)
    markdowns, others = util.find_files(config)
