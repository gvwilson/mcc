"""Check functionality for McCole."""

from pathlib import Path
import click

from . import util


def do_check(config, verbose, src, dst):
    """Check the site for errors."""
    config_file = Path(config) if config else util.DEFAULT_CONFIG_PATH
    config = util.read_config(config_file, verbose, src, dst)
    markdowns, others = util.find_files(config)
